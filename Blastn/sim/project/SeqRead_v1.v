//=========================================================================
// seqeucne read unit
//=========================================================================
// Extend array is packed in 2 bit wide and stored in a 32bit INT

`ifndef PROJECT_BLASTN_SEQ_READ_V1_V
`define PROJECT_BLASTN_SEQ_READ_V1_V

`include "vc/trace.v"
`include "vc/queues.v"

module project_SeqRead_v1
(
  input logic clk,
  input logic reset,
  
  // control unit interface
  input  logic [127:0]  istream_msg, // db_pos,q_pos,db_seq, q_seq
  input  logic          istream_val,
  output logic          istream_rdy,

  // UGPE interface
  input  logic        ostream_rdy,
  output logic        ostream_val,
  output logic [127:0] ostream_msg // len, hit, dstart, qbstart, d, q
);

localparam STATE_IDLE = 3'd0;
localparam STATE_RECEIVE_CTRL = 3'd1;
localparam STATE_UGPE_SEND = 3'd2;
localparam STATE_UGPE_WAIT = 3'd3;

logic [127:0] istream_reg, istream_reg_next;
logic [127:0] ostream_msg_reg, ostream_msg_reg_next;

logic [2:0] state_reg;

logic [31:0] query_seq, db_seq;
logic [31:0] q_pos, db_pos;

logic [15:0] hit_pos, seq_len;
logic [31:0] new_query, new_db;

assign query_seq = istream_reg[31:0];
assign db_seq = istream_reg[63:32];
assign q_pos = istream_reg[95:64];
assign db_pos = istream_reg[127:96];

assign ostream_msg = ostream_msg_reg & {127{ostream_val}};

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
          state_reg <= STATE_UGPE_SEND;
      end

      STATE_UGPE_SEND: begin
        state_reg <= STATE_UGPE_WAIT;
      end

      STATE_UGPE_WAIT: begin
        if (ostream_rdy) begin
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
  end
  else begin
    istream_reg <= istream_reg_next;
    ostream_msg_reg <= ostream_msg_reg_next;
  end
end

always_comb begin
  istream_rdy = 1'b0;
  ostream_val = 1'b0;

  ostream_msg_reg_next = ostream_msg_reg;
  istream_reg_next = istream_reg;
  hit_pos = 0;
  seq_len = 0;
  new_query = 0;
  new_db = 0;

  if (state_reg == STATE_RECEIVE_CTRL) begin
    istream_rdy = 1'b1;
    istream_reg_next = istream_msg;
  end
  else if (state_reg == STATE_UGPE_SEND) begin
    // use mask and shift to 
    if( q_pos > db_pos) begin
      hit_pos = db_pos;
      seq_len = q_pos - db_pos;
      seq_len = 16 - seq_len;
      // use mask to get the correct bits
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
    ostream_msg_reg_next[127:112] = seq_len;
    ostream_msg_reg_next[111:96] = hit_pos;
    ostream_msg_reg_next[95:80] = db_pos;
    ostream_msg_reg_next[79:64] = q_pos;
    ostream_msg_reg_next[63:32] = new_db;
    ostream_msg_reg_next[31:0] = new_query;
  end
  else if (state_reg == STATE_UGPE_WAIT) begin
    ostream_val = 1'b1;
  end
  
end



//----------------------------------------------------------------------
// Line Tracing
//----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin
    vc_trace.append_str( trace_str, "(" );
    vc_trace.append_str( trace_str, "--" );
    case ( state_reg )
      STATE_IDLE:               vc_trace.append_str( trace_str, "X " );
      STATE_RECEIVE_CTRL:       vc_trace.append_str( trace_str, "Receive" );
      STATE_UGPE_SEND:          vc_trace.append_str( trace_str, "US " );
      STATE_UGPE_WAIT:          vc_trace.append_str( trace_str, "W " );
      default:                  vc_trace.append_str( trace_str, "? " );
    endcase
  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */


endmodule

`endif // PROJECT_BLASTN_SEQ_READ_V1_V