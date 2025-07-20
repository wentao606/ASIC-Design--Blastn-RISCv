`ifndef PROJECT_BLASTN_XCEL_V1_V
`define PROJECT_BLASTN_XCEL_V1_V

`include "vc/trace.v"
`include "vc/xcel-msgs.v"
`include "vc/mem-msgs.v"
`include "vc/queues.v"
`include "project/SeqRead_v1.v"
`include "project/UGPE_v1.v"
`include "project/control_unit_v1.v"

module project_BlastnXcel_v1
(
  input  logic        clk,
  input  logic        reset,

  // xcel interface
  input  xcel_req_t   xcel_reqstream_msg,
  input  logic        xcel_reqstream_val,
  output logic        xcel_reqstream_rdy,

  output xcel_resp_t  xcel_respstream_msg,
  output logic        xcel_respstream_val,
  input  logic        xcel_respstream_rdy,

  // memory interface
  output mem_req_4B_t  mem_reqstream_msg,
  output logic         mem_reqstream_val,
  input  logic         mem_reqstream_rdy,

  input  mem_resp_4B_t mem_respstream_msg,
  input  logic         mem_respstream_val,
  output logic         mem_respstream_rdy
);

  // xcel_resp_t   xcel_respstream_msg_raw;
  mem_req_4B_t mem_reqstream_msg_raw;

  // assign xcel_respstream_msg = xcel_respstream_msg_raw & {$bits(xcel_resp_t){xcel_respstream_val}};
  assign mem_reqstream_msg   = mem_reqstream_msg_raw & {$bits(mem_req_4B_t){mem_reqstream_val}};
  always_ff @(posedge clk) begin
    if (reset) begin
      mem_reqstream_val <=  0;
      mem_respstream_rdy <= 0;
    end
    else begin
      mem_reqstream_val <=  0;
      mem_respstream_rdy <= 0;
    end
  end

  logic [127:0] cu_to_seq_msg;
  logic         cu_to_seq_val;
  logic         seq_to_cu_rdy;

  logic [127:0] seq_to_ugpe_msg;
  logic         seq_to_ugpe_val;
  logic         ugpe_to_seq_rdy;

  logic         ugpe_out_val;
  logic [31:0]  ugpe_out_msg;
  logic         ugpe_in_rdy;


  //----------------------------------------------------------------------
  // Control Unit
  //----------------------------------------------------------------------
  project_blastn_control_unit_V1 control_unit (
    .clk                 (clk),
    .reset               (reset),

    .xcel_reqstream_msg  (xcel_reqstream_msg),
    .xcel_reqstream_val  (xcel_reqstream_val),
    .xcel_reqstream_rdy  (xcel_reqstream_rdy),

    .xcel_respstream_msg (xcel_respstream_msg),
    .xcel_respstream_val (xcel_respstream_val),
    .xcel_respstream_rdy (xcel_respstream_rdy),

    .ostream_val         (cu_to_seq_val),
    .ostream_rdy         (seq_to_cu_rdy),
    .ostream_msg         (cu_to_seq_msg),

    .istream_msg         (ugpe_out_msg),
    .istream_val         (ugpe_out_val),
    .istream_rdy         (ugpe_in_rdy)

  );

  //----------------------------------------------------------------------
  // Sequence Reader
  //----------------------------------------------------------------------

  project_SeqRead_v1 seq_reader (
    .clk           (clk),
    .reset         (reset),

    .istream_msg   (cu_to_seq_msg),
    .istream_val   (cu_to_seq_val),
    .istream_rdy   (seq_to_cu_rdy),

    .ostream_val   (seq_to_ugpe_val),
    .ostream_rdy   (ugpe_to_seq_rdy),
    .ostream_msg   (seq_to_ugpe_msg)
  );

  //----------------------------------------------------------------------
  // UGPE Unit
  //----------------------------------------------------------------------

  project_UGPE_v1 ugpe (
    .clk           (clk),
    .reset         (reset),

    .istream_val   (seq_to_ugpe_val),
    .ostream_rdy   (ugpe_in_rdy),
    .istream_msg   (seq_to_ugpe_msg),

    .ostream_val   (ugpe_out_val),
    .istream_rdy   (ugpe_to_seq_rdy),
    .ostream_msg   (ugpe_out_msg)
  );
//----------------------------------------------------------------------
// Line Tracing
//----------------------------------------------------------------------

  `ifndef SYNTHESIS

  vc_XcelReqMsgTrace xcel_reqstream_msg_trace
  (
    .clk (clk),
    .reset (reset),
    .val   (xcel_reqstream_val),
    .rdy   (xcel_reqstream_rdy),
    .msg   (xcel_reqstream_msg)
  );

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin
    xcel_reqstream_msg_trace.line_trace( trace_str );
    vc_trace.append_str( trace_str, "(" );
    vc_trace.append_str( trace_str, "--" );
    control_unit.line_trace( trace_str );
    vc_trace.append_str( trace_str, ")" );

    vc_trace.append_str( trace_str, "(" );
    vc_trace.append_str( trace_str, "--" );
    ugpe.line_trace( trace_str );
    vc_trace.append_str( trace_str, ")" );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */
endmodule

`endif //PROJECT_BLASTN_XCEL_V1_V