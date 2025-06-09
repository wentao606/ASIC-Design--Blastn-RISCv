//=========================================================================
// seqeucne read unit
//=========================================================================
// Extend array is packed in 2 bit wide and stored in a 32bit INT

`ifndef PROJECT_BLASTN_SEQ_READ_V2_V
`define PROJECT_BLASTN_SEQ_READ_V2_V

`include "vc/trace.v"
`include "vc/queues.v"

module project_SeqRead_v2
(
  input logic clk,
  input logic reset,
  
  // control unit interface
  input  logic [255:0]  istream_msg, // db_pos,q_pos,db_seq, q_seq
  input  logic          istream_val,
  output logic          istream_rdy,

  // UGPE interface
  input  logic        ostream1_rdy,
  output logic        ostream1_val,
  input  logic        ostream2_rdy,
  output logic        ostream2_val,
  output logic [255:0] ostream_msg, // scoreaddr, lenaddr, db_posaddr, q_posaddr, len, hit, dstart, qstart, d, q

  // memory interface 
  output logic [31:0]  sr_req_istream_msg,

  output logic         sr_req_istream_val,
  input logic        sr_req_istream_rdy,

  input logic        sr_resp_istream_val,
  output logic         sr_resp_istream_rdy,

  input logic [31:0] sr_resp_istream_msg
);

localparam STATE_IDLE = 4'd0;
localparam STATE_RECEIVE_CTRL = 4'd1;
localparam STATE_SEND_MEM = 4'd2;
localparam STATE_REC_MEM = 4'd3;
localparam STATE_UGPE_SEND = 4'd4;
localparam STATE_UGPE_WAIT = 4'd5;


logic [255:0] istream_reg, istream_reg_next;
logic [255:0] ostream_msg_reg, ostream_msg_reg_next;

logic [3:0] state_reg;

logic [31:0] query_seq, db_seq, db_addr, db_seq_next;
logic [31:0] q_pos, db_pos;

logic [15:0] hit_pos, seq_len;
logic [31:0] new_query, new_db;

logic [31:0] sr_resp_istream_msg_reg, sr_resp_istream_msg_reg_next;

assign query_seq = istream_reg[31:0];
assign db_addr = istream_reg[63:32];
assign q_pos = istream_reg[95:64];
assign db_pos = istream_reg[127:96];

assign ostream_msg = ostream_msg_reg & {256{ostream1_val || ostream2_val}};

always_ff @(posedge clk) begin
  if (reset) begin
    state_reg <= STATE_IDLE;
  end 
  else begin
    state_reg <= state_reg;
    case (state_reg)
      STATE_IDLE: begin
        if (istream_val) begin
          state_reg <= STATE_RECEIVE_CTRL;
        end
      end

      STATE_RECEIVE_CTRL: begin
          state_reg <= STATE_SEND_MEM;
      end

      STATE_SEND_MEM: begin
        if(sr_req_istream_rdy) begin
          state_reg <= STATE_REC_MEM;
        end
      end

      STATE_REC_MEM: begin
        if (sr_resp_istream_val) begin
          state_reg <= STATE_UGPE_SEND;
        end
      end

      STATE_UGPE_SEND: begin
        state_reg <= STATE_UGPE_WAIT;
      end

      STATE_UGPE_WAIT: begin
        if (ostream1_rdy || ostream2_rdy) begin
          state_reg <= STATE_IDLE;
        end
      end

      default: state_reg <= STATE_IDLE;
    endcase
  end
end

always_ff @(posedge clk) begin
  if (reset) begin
    istream_reg <= 0;
    ostream_msg_reg <= 0;
    db_seq <= 0;
  end
  else begin
    istream_reg <= istream_reg_next;
    ostream_msg_reg <= ostream_msg_reg_next;
    db_seq <= db_seq_next;
    // db_seq_next <= sr_resp_istream_msg_reg;
  end
end

always_comb begin
  istream_rdy = 1'b0;
  ostream1_val = 1'b0;
  ostream2_val = 1'b0;
  sr_req_istream_msg = 0;       
  sr_resp_istream_rdy = 0; 

  ostream_msg_reg_next = ostream_msg_reg;
  istream_reg_next = istream_reg;
  sr_req_istream_val = 1'b0;
  db_seq_next = db_seq;
  hit_pos = 0;
  seq_len = 0;
  new_query = 0;
  new_db = 0;

  if (state_reg == STATE_RECEIVE_CTRL) begin
    istream_rdy = 1'b1;
    istream_reg_next = istream_msg;
  end
  
  else if (state_reg == STATE_SEND_MEM) begin
    sr_req_istream_val = 1;
    sr_req_istream_msg = istream_reg[63:32];
  end

  else if (state_reg == STATE_REC_MEM) begin
    sr_resp_istream_rdy = 1;
    if (sr_resp_istream_val) begin
      db_seq_next = sr_resp_istream_msg;
    end
  end

  else if (state_reg == STATE_UGPE_SEND) begin
    if( q_pos > db_pos) begin
      hit_pos = db_pos;
      seq_len = q_pos - db_pos;
      seq_len = 16 - seq_len;
      // use mask to get the right bits
      new_db = db_seq & (32'hFFFFFFFF >> (32 - ((seq_len << 1))));
      new_query = (query_seq >> ((q_pos - hit_pos) << 1)) 
              & (32'hFFFFFFFF >> ((q_pos - hit_pos) << 1));
    end
    else begin
      hit_pos = q_pos;
      seq_len = db_pos - q_pos;
      seq_len = 16 - seq_len;
      new_db = (db_seq >> ((db_pos - hit_pos) << 1)) 
              & (32'hFFFFFFFF >> ((db_pos - hit_pos) << 1));
      new_query = query_seq & (32'hFFFFFFFF >> (32 - ((seq_len << 1))));
    end
    // len, hit, dstart, qbstart, d, q
    ostream_msg_reg_next[255:128] = istream_reg[255:128];
    ostream_msg_reg_next[127:112] = seq_len;
    ostream_msg_reg_next[111:96] = hit_pos;
    ostream_msg_reg_next[95:80] = db_pos;
    ostream_msg_reg_next[79:64] = q_pos;
    ostream_msg_reg_next[63:32] = new_db;
    ostream_msg_reg_next[31:0] = new_query;
  end

  else if (state_reg == STATE_UGPE_WAIT) begin
    if(ostream1_rdy) begin
      ostream1_val = 1'b1;
    end
    else if (ostream2_rdy) begin
      ostream2_val = 1'b1;
    end
    // ostream1_val = 1'b1;
    // ostream2_val = 1'b1;

  end
  
end



//----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin
    // xcel_reqstream_msg_trace.line_trace( trace_str );

    vc_trace.append_str( trace_str, "(" );
    vc_trace.append_str( trace_str, "--" );
    case ( state_reg )
      STATE_IDLE:           vc_trace.append_str( trace_str, "IDLE     " );
      STATE_RECEIVE_CTRL:   vc_trace.append_str( trace_str, "RECEIVE  " );
      STATE_SEND_MEM:       vc_trace.append_str( trace_str, "SEND_MEM " );
      STATE_REC_MEM:        vc_trace.append_str( trace_str, "REC_MEM  " );
      STATE_UGPE_SEND:      vc_trace.append_str( trace_str, "UGPE_SEND" );
      STATE_UGPE_WAIT:      vc_trace.append_str( trace_str, "UGPE_WAIT" );
      default:              vc_trace.append_str( trace_str, "UNKNOWN  " );
    endcase


    // $sformat( str, "isnxt:%x  ", istream_reg_next);
    // vc_trace.append_str( trace_str, str );

    // $sformat( str, "qp:%x ", q_pos);
    // vc_trace.append_str( trace_str, str );

    // $sformat( str, "dp:%x ", db_pos);
    // vc_trace.append_str( trace_str, str );

    // $sformat( str, "hp:%x ", hit_pos);
    // vc_trace.append_str( trace_str, str );

    // $sformat( str, "len:%d ", seq_len);
    // vc_trace.append_str( trace_str, str );





    // xcel_respstream_msg_trace.line_trace( trace_str );
  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */


endmodule

`endif // PROJECT_BLASTN_SEQ_READ_V2_V