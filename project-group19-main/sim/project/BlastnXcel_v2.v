`ifndef PROJECT_BLASTN_XCEL_V2_V
`define PROJECT_BLASTN_XCEL_V2_V

`include "vc/trace.v"
`include "vc/xcel-msgs.v"
`include "vc/mem-msgs.v"
`include "vc/queues.v"
`include "project/SeqRead_v2.v"
`include "project/UGPE_v2.v"
`include "project/control_unit_v2.v"
`include "project/memory_itf.v"

module project_BlastnXcel_v2
(
  input  logic         clk,
  input  logic         reset,

  // Accelerator interface
  input  xcel_req_t    xcel_reqstream_msg,
  input  logic         xcel_reqstream_val,
  output logic         xcel_reqstream_rdy,

  output xcel_resp_t   xcel_respstream_msg,
  output logic         xcel_respstream_val,
  input  logic         xcel_respstream_rdy,

  // Memory interface
  output mem_req_4B_t  mem_reqstream_msg,
  output logic         mem_reqstream_val,
  input  logic         mem_reqstream_rdy,

  input  mem_resp_4B_t mem_respstream_msg,
  input  logic         mem_respstream_val,
  output logic         mem_respstream_rdy
);


  //==============================
  // Internal wires
  //==============================

  // Control to SeqRead
  logic [255:0] istream_msg;
  logic         istream_val;
  logic         istream_rdy;
  logic [4:0]   ctrl_state;

  // SeqRead t0 UGPE
  logic         ostream1_val, ostream1_rdy;
  logic         ostream2_val, ostream2_rdy;
  logic [255:0] ostream_msg;

  // UGPE t0 MemAccess
  logic         ugpe1_out_val, ugpe1_out_rdy;
  logic [159:0] ugpe1_out_msg;

  logic         ugpe2_out_val, ugpe2_out_rdy;
  logic [159:0] ugpe2_out_msg;

  logic [159:0] selected_ugpe_msg;
  assign selected_ugpe_msg = ugpe1_out_val ? ugpe1_out_msg : ugpe2_out_msg;

  // SeqRead  MemAccess
  logic [31:0] sr_req_istream_msg;
  logic         sr_req_istream_val;
  logic         sr_req_istream_rdy;

  logic [31:0] sr_resp_istream_msg;
  logic         sr_resp_istream_val;
  logic         sr_resp_istream_rdy;

  logic done;

  //==============================
  // Control Unit
  //==============================
  project_blastn_control_unit_V2 control_unit (
    .clk(clk),
    .reset(reset),

    .xcel_reqstream_msg(xcel_reqstream_msg),
    .xcel_reqstream_val(xcel_reqstream_val),
    .xcel_reqstream_rdy(xcel_reqstream_rdy),

    .xcel_respstream_msg(xcel_respstream_msg),
    .xcel_respstream_val(xcel_respstream_val),
    .xcel_respstream_rdy(xcel_respstream_rdy),

    .ostream_val(istream_val),
    .ostream_rdy(istream_rdy),
    .ostream_msg(istream_msg),
    .state_reg(ctrl_state),

    .done(done)
  );

  //==============================
  // Sequence Read Unit
  //==============================
  project_SeqRead_v2 seq_reader (
    .clk(clk),
    .reset(reset),

    .istream_msg(istream_msg),
    .istream_val(istream_val),
    .istream_rdy(istream_rdy),

    .ostream1_val(ostream1_val),
    .ostream1_rdy(ostream1_rdy),
    .ostream2_val(ostream2_val),
    .ostream2_rdy(ostream2_rdy),
    .ostream_msg(ostream_msg),

    .sr_req_istream_msg(sr_req_istream_msg),
    .sr_req_istream_val(sr_req_istream_val),
    .sr_req_istream_rdy(sr_req_istream_rdy),

    .sr_resp_istream_msg(sr_resp_istream_msg),
    .sr_resp_istream_val(sr_resp_istream_val),
    .sr_resp_istream_rdy(sr_resp_istream_rdy)
  );

  //==============================
  // UGPE 1
  //==============================
  project_UGPE_v2 ugpe1 (
    .clk(clk),
    .reset(reset),
    .istream_val(ostream1_val),
    .istream_msg(ostream_msg),
    .istream_rdy(ostream1_rdy),
    .ostream_val(ugpe1_out_val),
    .ostream_msg(ugpe1_out_msg),
    .ostream_rdy(ugpe1_out_rdy)
  );

  //==============================
  // UGPE 2
  //==============================
  project_UGPE_v2 ugpe2 (
    .clk(clk),
    .reset(reset),
    .istream_val(ostream2_val),
    .istream_msg(ostream_msg),
    .istream_rdy(ostream2_rdy),
    .ostream_val(ugpe2_out_val),
    .ostream_msg(ugpe2_out_msg),
    .ostream_rdy(ugpe2_out_rdy)
  );

  //==============================
  // Memory Access Unit
  //==============================
  project_blastn_memory_access mem_access (
    .clk(clk),
    .reset(reset),

    .ugpe_istream_msg(selected_ugpe_msg),
    .ugpe_istream1_val(ugpe1_out_val),
    .ugpe_istream1_rdy(ugpe1_out_rdy),
    .ugpe_istream2_val(ugpe2_out_val),
    .ugpe_istream2_rdy(ugpe2_out_rdy),

    .sr_req_istream_msg(sr_req_istream_msg),
    .sr_req_istream_val(sr_req_istream_val),
    .sr_req_istream_rdy(sr_req_istream_rdy),
    .sr_resp_istream_msg(sr_resp_istream_msg),
    .sr_resp_istream_val(sr_resp_istream_val),
    .sr_resp_istream_rdy(sr_resp_istream_rdy),

    .mem_reqstream_msg(mem_reqstream_msg),
    .mem_reqstream_val(mem_reqstream_val),
    .mem_reqstream_rdy(mem_reqstream_rdy),
    .mem_respstream_msg(mem_respstream_msg),
    .mem_respstream_val(mem_respstream_val),
    .mem_respstream_rdy(mem_respstream_rdy),

    .done(done)
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
    seq_reader.line_trace( trace_str );
    vc_trace.append_str( trace_str, ")" );

    vc_trace.append_str( trace_str, "(" );
    vc_trace.append_str( trace_str, "--" );
    ugpe1.line_trace( trace_str );
    vc_trace.append_str( trace_str, ")" );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif // PROJECT_BLASTN_XCEL_V2_V
