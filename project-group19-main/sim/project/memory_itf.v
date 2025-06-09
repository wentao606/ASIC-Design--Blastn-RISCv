//=========================================================================
// memory access unit
//=========================================================================
// Extend array is packed in 2 bit wide and stored in a 32bit INT

`ifndef PROJECT_BLASTN_MEMORY_ACCESS_V
`define PROJECT_BLASTN_MEMORY_ACCESS_V

`include "vc/trace.v"

`include "vc/mem-msgs.v"
`include "vc/queues.v"

module project_blastn_memory_access
(
  input logic clk,
  input logic reset,

  // interface with ugpes
  // msg: [addrscore, addrlen, addrdstart, addrqstart]:4*32 + 32[d_start, q_start, len, score]
  input logic [159:0]  ugpe_istream_msg,

  // assume we only have two ugpes
  input logic         ugpe_istream1_val,
  output logic        ugpe_istream1_rdy,

  input logic         ugpe_istream2_val,
  output logic        ugpe_istream2_rdy,

  // seq reader interface
  input logic [31:0]  sr_req_istream_msg,

  input logic         sr_req_istream_val,
  output logic        sr_req_istream_rdy,

  output logic        sr_resp_istream_val,
  input logic         sr_resp_istream_rdy,

  output logic [31:0] sr_resp_istream_msg,

  // memory interface, connected to memory
  output mem_req_4B_t  mem_reqstream_msg,
  output logic         mem_reqstream_val,
  input  logic         mem_reqstream_rdy,

  input  mem_resp_4B_t mem_respstream_msg,
  input  logic         mem_respstream_val,
  output logic         mem_respstream_rdy,

  output logic        done

);

  mem_req_4B_t mem_reqstream_msg_raw;
  assign mem_reqstream_msg   = mem_reqstream_msg_raw & {$bits(mem_req_4B_t){mem_reqstream_val}};

  // Memory ports and queues

  logic         memresp_deq_val;
  logic         memresp_deq_rdy;
  mem_resp_4B_t memresp_deq_msg;

  vc_Queue#(`VC_QUEUE_PIPE,$bits(mem_resp_4B_t),1) memresp_q
  (
    .clk     (clk),
    .reset   (reset),
    .num_free_entries(),

    .enq_val (mem_respstream_val),
    .enq_rdy (mem_respstream_rdy),
    .enq_msg (mem_respstream_msg),

    .deq_val (memresp_deq_val),
    .deq_rdy (memresp_deq_rdy),
    .deq_msg (memresp_deq_msg)
  );

  localparam STATE_IDLE = 4'd0;
  localparam STATE_READ = 4'd1;
  localparam STATE_RWAIT = 4'd2;
  localparam STATE_SEND  = 4'd3;
  localparam STATE_WRITE = 4'd4;
  localparam STATE_WWAIT = 4'd5;

  logic [3:0] state_reg;
  logic [2:0] count, count_next;
  logic go_read;
  logic go_write;
  logic [159:0] ugpe_istream_msg_reg, ugpe_istream_msg_reg_next;
  logic [31:0] sr_addr_reg, sr_addr_reg_next;
  logic [31:0] sr_resp_msg_reg, sr_resp_msg_reg_next;

  always_ff @(posedge clk) begin
    if (reset) begin
      ugpe_istream_msg_reg <= 0;
      sr_addr_reg <= 0;
      sr_resp_msg_reg <= 0;
    end
    else begin
      ugpe_istream_msg_reg <= ugpe_istream_msg_reg_next;
      sr_addr_reg <= sr_addr_reg_next;
      sr_resp_msg_reg <= sr_resp_msg_reg_next;
    end
  end

  always_ff @(posedge clk) begin
    if (reset) begin
      state_reg <= 0;
      count <= 0; 
    end
    else begin
      state_reg <= state_reg;
      case (state_reg) 
        STATE_IDLE:begin
          count <= 0; 
          if (go_write)
            state_reg <= STATE_WRITE;
          else if (go_read)
            state_reg <= STATE_READ;
        end
        STATE_READ: begin
          if (mem_reqstream_rdy) begin
            state_reg <= STATE_RWAIT;
          end
        end
        STATE_RWAIT: begin
          if ( memresp_deq_val ) begin
            state_reg  <= STATE_SEND;
          end
        end
        STATE_SEND: begin
          if (sr_resp_istream_val) begin
            state_reg <= STATE_IDLE;
          end
        end
        STATE_WRITE: begin
          if (mem_reqstream_rdy) begin
            state_reg <= STATE_WWAIT;
          end
        end
        STATE_WWAIT: begin
          if (memresp_deq_val && count == 3'd3) begin
            state_reg <= STATE_IDLE;
          end
          else if (memresp_deq_val) begin
            count <= count + 1;
            state_reg <= STATE_WRITE;
          end
        end

        default: state_reg <= STATE_IDLE;

      endcase
    end
  end

  always_comb begin
    sr_req_istream_rdy = 1'b0;
    sr_resp_istream_val = 1'b0;
    sr_resp_istream_msg    = 32'b0;
    ugpe_istream1_rdy = 1'b0;
    ugpe_istream2_rdy = 1'b0;    
    go_read           = 1'b0;
    go_write          = 1'b0;
    mem_reqstream_val       = 0;
    mem_reqstream_msg_raw   = '0;
    memresp_deq_rdy         = 0;
    done                    = 0;

    ugpe_istream_msg_reg_next = ugpe_istream_msg_reg;
    sr_addr_reg_next          = sr_addr_reg;
    sr_resp_msg_reg_next      = sr_resp_msg_reg;


    if ( state_reg == STATE_IDLE ) begin
      if (sr_req_istream_val) begin
        sr_req_istream_rdy = 1'b1;
        go_read = 1'b1;
        sr_addr_reg_next = sr_req_istream_msg;
      end
      else if (ugpe_istream1_val) begin
        ugpe_istream1_rdy = 1'b1;
        go_write = 1'b1;
        ugpe_istream_msg_reg_next = ugpe_istream_msg;
        
      end
      else if (ugpe_istream2_val) begin
        ugpe_istream2_rdy = 1'b1;
        go_write = 1'b1;
        ugpe_istream_msg_reg_next = ugpe_istream_msg;
      end
    end

    else if ( state_reg == STATE_READ ) begin
      mem_reqstream_val = 1;

      mem_reqstream_msg_raw.type_  = `VC_MEM_REQ_MSG_TYPE_READ;
      mem_reqstream_msg_raw.opaque = 0;
      mem_reqstream_msg_raw.addr   = sr_addr_reg;
      mem_reqstream_msg_raw.len    = 0;
      mem_reqstream_msg_raw.data   = 0;
    end

    else if ( state_reg == STATE_RWAIT ) begin
      memresp_deq_rdy = 1;
      if ( memresp_deq_val ) begin
        sr_resp_msg_reg_next = memresp_deq_msg.data;
      end
    end

    else if ( state_reg == STATE_SEND ) begin
      sr_resp_istream_val = 1;
      sr_resp_istream_msg = sr_resp_msg_reg;
    end

    else if ( state_reg == STATE_WRITE ) begin
      mem_reqstream_val = 1;
      mem_reqstream_msg_raw.type_  = `VC_MEM_REQ_MSG_TYPE_WRITE;
      mem_reqstream_msg_raw.opaque = count;
      mem_reqstream_msg_raw.len    = 0;

      if (count == 0) begin
        mem_reqstream_msg_raw.data   = {24'b0, ugpe_istream_msg_reg[7:0]};
        mem_reqstream_msg_raw.addr   = ugpe_istream_msg_reg[63:32];
      end
      else if (count == 1) begin
        mem_reqstream_msg_raw.data   = {24'b0, ugpe_istream_msg_reg[15:8]};
        mem_reqstream_msg_raw.addr   = ugpe_istream_msg_reg[95:64];
      end
      else if (count == 2) begin
        mem_reqstream_msg_raw.data   = {24'b0, ugpe_istream_msg_reg[23:16]};
        mem_reqstream_msg_raw.addr   = ugpe_istream_msg_reg[127:96];
      end
      else if (count == 3) begin
        mem_reqstream_msg_raw.data   = {24'b0, ugpe_istream_msg_reg[31:24]};
        mem_reqstream_msg_raw.addr   = ugpe_istream_msg_reg[159:128];
      end
      else begin
        mem_reqstream_msg_raw.data = 32'b0;
        mem_reqstream_msg_raw.addr = 32'b0;
      end
    end

    else if ( state_reg == STATE_WWAIT ) begin
      memresp_deq_rdy = 1;
      if (memresp_deq_val && count == 3'd3) begin
            done = 1;
          end
    end

  end

  

endmodule

`endif //PROJECT_BLASTN_MEMORY_ACCESS_V
