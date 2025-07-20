//=========================================================================
// control unit
//=========================================================================
// Extend array is packed in 2 bit wide and stored in a 32bit INT

`ifndef PROJECT_BLASTN_CONTROL_UNIT_V2_V
`define PROJECT_BLASTN_CONTROL_UNIT_V2_V

`include "vc/trace.v"
`include "vc/xcel-msgs.v"

module project_blastn_control_unit_V2
(
  input logic clk,
  input logic reset,

  // xcel interface
  input  xcel_req_t    xcel_reqstream_msg,
  input  logic         xcel_reqstream_val,
  output logic         xcel_reqstream_rdy,

  output xcel_resp_t   xcel_respstream_msg,
  output logic         xcel_respstream_val,
  input  logic         xcel_respstream_rdy,

  // to sequence reader
  output logic       ostream_val,
  input logic        ostream_rdy,
  output logic [255:0] ostream_msg, // dp_pos q_pos db_seq q_seq
  output logic [4:0] state_reg,

  input logic done

);

  xcel_resp_t  xcel_respstream_msg_raw;
  assign xcel_respstream_msg = xcel_respstream_msg_raw & {$bits(xcel_resp_t){xcel_respstream_val}};


  // output 
  logic [31:0] query_seq, query_seq_next;
  logic [31:0] db_seq, db_seq_next;
  logic [31:0] q_pos, q_pos_next;
  logic [31:0] db_pos, db_pos_next;
  logic [31:0] score_addr, score_addr_next, len_addr, len_addr_next;
  logic [31:0] db_pos_addr, db_pos_addr_next, q_pos_addr, q_pos_addr_next;
  logic [255:0] ostream_msg_reg, ostream_msg_reg_next;
  // logic [31:0] size, size_next;
  
  assign ostream_msg = ostream_msg_reg & 
                        {256{ostream_val}};

  // Accelerator ports and queues
 
  logic      xcelreq_deq_val;
  logic      xcelreq_deq_rdy;
  xcel_req_t xcelreq_deq_msg;

  vc_Queue#(`VC_QUEUE_PIPE,$bits(xcel_req_t),1) xcelreq_q
  (
    .clk     (clk),
    .reset   (reset),
    .num_free_entries(),

    .enq_val (xcel_reqstream_val),
    .enq_rdy (xcel_reqstream_rdy),
    .enq_msg (xcel_reqstream_msg),

    .deq_val (xcelreq_deq_val),
    .deq_rdy (xcelreq_deq_rdy),
    .deq_msg (xcelreq_deq_msg)
  );

  localparam STATE_XCFG = 4'd0;
  localparam STATE_SEND = 4'd1;
  localparam STATE_WAIT = 4'd2;
  localparam STATE_WAIT_MEM = 4'd3;

  // logic [4:0] state_reg;
  logic       go;

  // store the output
  always_ff @(posedge clk) begin
    if ( reset ) begin
      ostream_msg_reg <= 0;
      query_seq      <= 0;
      db_seq         <= 0;
      q_pos          <= 0;
      db_pos         <= 0;
    end
    else begin
      q_pos        <= q_pos_next;
      db_pos        <= db_pos_next;
      ostream_msg_reg <= ostream_msg_reg_next;
      query_seq      <= query_seq_next;
      db_seq         <= db_seq_next;
      score_addr      <= score_addr_next;
      len_addr        <= len_addr_next;
      db_pos_addr     <= db_pos_addr_next;
      q_pos_addr      <= q_pos_addr_next;
    end
  end

  always_ff @(posedge clk) begin
    if ( reset ) begin
      state_reg <= STATE_XCFG;
    end
    else begin
      state_reg <= state_reg;

      case ( state_reg )

        STATE_XCFG:
          if ( go & xcel_respstream_rdy ) begin
            state_reg <= STATE_SEND;
          end

        STATE_SEND:
          state_reg <= STATE_WAIT;

        STATE_WAIT:
          if ( ostream_rdy ) begin
            state_reg  <= STATE_WAIT_MEM;
          end
        
        STATE_WAIT_MEM:
          if (done) begin
            state_reg <= STATE_XCFG;
          end

        default:
          state_reg <= STATE_XCFG;
      endcase
    end
  end
  always_comb begin

    xcelreq_deq_rdy     = 0;
    xcel_respstream_val = 0;
    xcel_respstream_msg_raw = '0;
    ostream_msg_reg_next = ostream_msg_reg;

    query_seq_next    = query_seq;
    db_seq_next       = db_seq;
    q_pos_next        = q_pos;
    db_pos_next       = db_pos;
    score_addr_next     = score_addr;
    len_addr_next       = len_addr;
    db_pos_addr_next    = db_pos_addr;
    q_pos_addr_next     = q_pos_addr;
    ostream_val       = 0;
    go                = 0;

    //--------------------------------------------------------------------
    // STATE: XCFG
    //--------------------------------------------------------------------
    // In this state we handle the accelerator configuration protocol,
    // where we write the base addresses, size, and then tell the
    // accelerator to start. We also handle responding when the
    // accelerator is done.

    if ( state_reg == STATE_XCFG ) begin
      xcelreq_deq_rdy     = xcel_respstream_rdy;
      xcel_respstream_val = xcelreq_deq_val;

      if ( xcelreq_deq_val ) begin

        // Send xcel response message, obviously you only want to
        // send the response message when accelerator is done

        if ( xcelreq_deq_msg.type_ == `VC_XCEL_REQ_MSG_TYPE_READ ) begin
          if (xcelreq_deq_msg.addr == 0) begin
            xcel_respstream_msg_raw.type_ = `VC_XCEL_RESP_MSG_TYPE_READ;
            xcel_respstream_msg_raw.data  = 1;
          end
        end
        else begin
          if ( xcelreq_deq_msg.addr == 0 ) begin
            go          = 1;
          end
          else if ( xcelreq_deq_msg.addr == 1 )
            query_seq_next = xcelreq_deq_msg.data;
          else if ( xcelreq_deq_msg.addr == 2 ) begin
            db_seq_next = xcelreq_deq_msg.data;
          end
          else if ( xcelreq_deq_msg.addr == 3 ) begin
            q_pos_next = xcelreq_deq_msg.data;
          end
          else if ( xcelreq_deq_msg.addr == 4 ) begin
            db_pos_next = xcelreq_deq_msg.data;
          end
          else if ( xcelreq_deq_msg.addr == 5 )
            score_addr_next = xcelreq_deq_msg.data;

          else if ( xcelreq_deq_msg.addr == 6 ) begin
            len_addr_next = xcelreq_deq_msg.data;
          end

          else if ( xcelreq_deq_msg.addr == 7 ) begin
            q_pos_addr_next = xcelreq_deq_msg.data;
          end

          else if ( xcelreq_deq_msg.addr == 8 ) begin 
            db_pos_addr_next = xcelreq_deq_msg.data;
          end

          xcel_respstream_msg_raw.type_ = `VC_XCEL_RESP_MSG_TYPE_WRITE;
          xcel_respstream_msg_raw.data  = 0;
        end
      end
    end
    else if (state_reg == STATE_SEND) begin
      ostream_msg_reg_next = {db_pos_addr, q_pos_addr, len_addr, score_addr, db_pos, q_pos, db_seq, query_seq};
    end
    else if (state_reg == STATE_WAIT) begin
      ostream_val = 1'b1;
    end

  end
 //======================================================================
  // Line Tracing
  //======================================================================

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
    begin
      case ( state_reg )
        STATE_XCFG:      vc_trace.append_str( trace_str, "X " );
        STATE_SEND:      vc_trace.append_str( trace_str, "SD" );
        STATE_WAIT:      vc_trace.append_str( trace_str, "W " );
        default:         vc_trace.append_str( trace_str, "? " );
      endcase
      vc_trace.append_str( trace_str, "(" );
      vc_trace.append_str( trace_str, "--" );

      // $sformat(str, "dp_pos:%x q_pos %x", db_pos, q_pos);
      // vc_trace.append_str( trace_str, str );

      // $sformat( str, "|oreg%x  ", ostream_msg_reg);
      // vc_trace.append_str( trace_str, str );

      $sformat( str, "|o:%x|", ostream_msg);
      // vc_trace.append_str( trace_str, str );

    end

  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule
`endif // PROJECT_BLASTN_CONTROL_UNIT_V2_V
