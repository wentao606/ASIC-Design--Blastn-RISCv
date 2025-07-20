//========================================================================
// Vector Vector Add Accelerator Verilog Implementation
//========================================================================
// Adds two vectors in memory together and stores result in memory.
// Accelerator register interface:
//
//  xr0 : go/done
//  xr1 : base address of the array src0
//  xr2 : base address of the array src1
//  xr3 : base address of the array dest
//  xr4 : size of the array
//
// Accelerator protocol involves the following steps:
//  1. Write the base address of src0 to xr1
//  2. Write the base address of src1 to xr2
//  3. Write the base address of dest to xr3
//  4. Write the number of elements in the array to xr4
//  5. Tell accelerator to go by writing xr0
//  6. Wait for accelerator to finish by reading xr0, result will be 1

`ifndef TUT9_XCEL_VVADD_XCEL_V
`define TUT9_XCEL_VVADD_XCEL_V

`include "vc/trace.v"

`include "vc/mem-msgs.v"
`include "vc/queues.v"
`include "vc/xcel-msgs.v"

//========================================================================
// Vector Vector Add Xcel Implementation
//========================================================================

module tut9_xcel_VvaddXcel
(
  input  logic          clk,
  input  logic          reset,

  input  xcel_req_t     xcel_reqstream_msg,
  input  logic          xcel_reqstream_val,
  output logic          xcel_reqstream_rdy,

  output xcel_resp_t    xcel_respstream_msg,
  output logic          xcel_respstream_val,
  input  logic          xcel_respstream_rdy,

  output mem_req_16B_t  mem_reqstream_msg,
  output logic          mem_reqstream_val,
  input  logic          mem_reqstream_rdy,

  input  mem_resp_16B_t mem_respstream_msg,
  input  logic          mem_respstream_val,
  output logic          mem_respstream_rdy
);

  // 4-state sim fix: force outputs to be zero if invalid

  xcel_resp_t   xcel_respstream_msg_raw;
  mem_req_16B_t mem_reqstream_msg_raw;

  assign xcel_respstream_msg = xcel_respstream_msg_raw & {$bits(xcel_resp_t){xcel_respstream_val}};
  assign mem_reqstream_msg   = mem_reqstream_msg_raw & {$bits(mem_req_16B_t){mem_reqstream_val}};

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

  // Memory ports and queues

  logic          memresp_deq_val;
  logic          memresp_deq_rdy;
  mem_resp_16B_t memresp_deq_msg;

  vc_Queue#(`VC_QUEUE_PIPE,$bits(mem_resp_16B_t),1) memresp_q
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

  // Extra state registers

  logic [3:0]  memreq_sent, memreq_sent_next;
  logic [3:0]  memrsp_recv, memrsp_recv_next;
  logic [31:0] idx,         idx_next;
  logic [31:0] size,        size_next;
  logic [31:0] base_src0,   base_src0_next;
  logic [31:0] base_src1,   base_src1_next;
  logic [31:0] base_dest,   base_dest_next;
  logic [31:0] num_src0,    num_src0_next;
  logic [31:0] num_src1,    num_src1_next;
  logic [31:0] sum_val,     sum_val_next;

  always_ff @(posedge clk) begin
    if (reset) begin
      memreq_sent <= 0;
      memrsp_recv <= 0;
      idx         <= 0;
      size        <= 0;
      base_src0   <= 0;
      base_src1   <= 0;
      base_dest   <= 0;
      num_src0    <= 0;
      num_src1    <= 0;
      sum_val     <= 0;
    end
    else begin
      memreq_sent <= memreq_sent_next;
      memrsp_recv <= memrsp_recv_next;
      idx         <= idx_next;
      size        <= size_next;
      base_src0   <= base_src0_next;
      base_src1   <= base_src1_next;
      base_dest   <= base_dest_next;
      num_src0    <= num_src0_next;
      num_src1    <= num_src1_next;
      sum_val     <= sum_val_next;
    end
  end

  //======================================================================
  // State Update
  //======================================================================

  localparam STATE_XCFG = 3'd0;
  localparam STATE_M_RD = 3'd1;
  localparam STATE_ADD  = 3'd2;
  localparam STATE_M_WR = 3'd3;
  localparam STATE_WAIT = 3'd4;

  logic [2:0] state_reg;
  logic go;

  always_ff @(posedge clk) begin

    if ( reset )
      state_reg <= STATE_XCFG;
    else begin
      state_reg <= state_reg;

      case ( state_reg )

        STATE_XCFG:
          if ( go && xcel_respstream_rdy )
            state_reg <= STATE_M_RD;

        STATE_M_RD:
          if ( memrsp_recv == 1 && memresp_deq_val )
            state_reg <= STATE_ADD;

        STATE_ADD:
          state_reg <= STATE_M_WR;

        STATE_M_WR:
          if ( mem_reqstream_rdy )
            state_reg <= STATE_WAIT;

        STATE_WAIT:
          if ( memresp_deq_val )
            if ( idx < size - 1 )
              state_reg <= STATE_M_RD;
            else
              state_reg <= STATE_XCFG;

        default:
          state_reg <= STATE_XCFG;

      endcase
    end
  end

  //======================================================================
  // State Outputs
  //======================================================================

  // Temporary
  logic [31:0] base_addr;

  always_comb begin

    xcelreq_deq_rdy     = 0;
    xcel_respstream_val = 0;
    mem_reqstream_val   = 0;
    memresp_deq_rdy     = 0;
    go                  = 0;

    memreq_sent_next    = memreq_sent;
    memrsp_recv_next    = memrsp_recv;
    idx_next            = idx;
    size_next           = size;
    base_src0_next      = base_src0;
    base_src1_next      = base_src1;
    base_dest_next      = base_dest;
    num_src0_next       = num_src0;
    num_src1_next       = num_src1;
    sum_val_next        = sum_val;

    base_addr               = '0;
    xcel_respstream_msg_raw = '0;
    mem_reqstream_msg_raw   = '0;

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
          xcel_respstream_msg_raw.type_ = `VC_XCEL_RESP_MSG_TYPE_READ;
          xcel_respstream_msg_raw.data  = 1;
        end
        else begin
          if ( xcelreq_deq_msg.addr == 0 ) begin
            go = 1;
            memreq_sent_next = 0;
            memrsp_recv_next = 0;
            idx_next = 0;
          end
          else if ( xcelreq_deq_msg.addr == 1 )
            base_src0_next = xcelreq_deq_msg.data;

          else if ( xcelreq_deq_msg.addr == 2 )
            base_src1_next = xcelreq_deq_msg.data;

          else if ( xcelreq_deq_msg.addr == 3 )
            base_dest_next = xcelreq_deq_msg.data;

          else if ( xcelreq_deq_msg.addr == 4 )
            size_next = xcelreq_deq_msg.data;

          xcel_respstream_msg_raw.type_ = `VC_XCEL_RESP_MSG_TYPE_WRITE;
          xcel_respstream_msg_raw.data  = 0;
        end
      end
    end

    //--------------------------------------------------------------------
    // STATE: M_RD
    //--------------------------------------------------------------------
    // Memory read stage. Read from vector src0[i] and src1[i]. Decouple
    // memory requests and responses and wait until sent both memreq and
    // received both memresp

    else if ( state_reg == STATE_M_RD )
    begin

      // Memory requests. Continue sending until have sent 2 memreq
      if ( memreq_sent < 2 )
      begin
        mem_reqstream_val = 1;

        if ( memreq_sent == 0 )
          base_addr = base_src0;
        else
          base_addr = base_src1;

        mem_reqstream_msg_raw.type_  = `VC_MEM_REQ_MSG_TYPE_READ;
        mem_reqstream_msg_raw.opaque = 0;
        mem_reqstream_msg_raw.addr   = base_addr + (idx << 2);
        mem_reqstream_msg_raw.len    = 4;
        mem_reqstream_msg_raw.data   = 0;

        if ( mem_reqstream_rdy )
          memreq_sent_next = memreq_sent + 1;
      end

      // Memory responses. Continue receiving until received 2 memresp
      memresp_deq_rdy = ( memreq_sent > 0 );
      if ( memresp_deq_val & memresp_deq_rdy )
      begin
        if ( memrsp_recv == 0 )
          num_src0_next = memresp_deq_msg.data;
        else if ( memrsp_recv == 1 )
          num_src1_next = memresp_deq_msg.data;

        memrsp_recv_next = memrsp_recv + 1;
      end
    end

    //--------------------------------------------------------------------
    // STATE: ADD
    //--------------------------------------------------------------------
    // Simply add enues from vectors together and save

    else if ( state_reg == STATE_ADD ) begin
      sum_val_next = num_src0 + num_src1;
    end

    //--------------------------------------------------------------------
    // STATE: M_WR
    //--------------------------------------------------------------------
    // Memory write stage. Send memreq to write to the destination memory
    // addr dest[i] the sum of src0[i] and src1[i]. Wait for response in
    // next state

    else if ( state_reg == STATE_M_WR ) begin
      mem_reqstream_val            = 1;
      mem_reqstream_msg_raw.type_  = `VC_MEM_REQ_MSG_TYPE_WRITE;
      mem_reqstream_msg_raw.opaque = 0;
      mem_reqstream_msg_raw.addr   = base_dest + (idx << 2);
      mem_reqstream_msg_raw.len    = 4;
      mem_reqstream_msg_raw.data   = sum_val;
    end

    //--------------------------------------------------------------------
    // STATE: WAIT
    //--------------------------------------------------------------------
    // Wait for memory response to come back. Need to wait just to clear
    // memory response. Note, this can definitely done more efficiently
    // such as using a counter of memresp to simply clear out (if there
    // are multiple writes in flight that need to be cleared out)

    else if ( state_reg == STATE_WAIT ) begin
      memreq_sent_next = 0;
      memrsp_recv_next = 0;
      num_src0_next    = 0;
      num_src1_next    = 0;
      sum_val_next     = 0;

      memresp_deq_rdy = 1;
      if ( memresp_deq_val ) begin

        // just throw away memresp
        // if idx < size - 1, still not through entire vector so increment
        if ( idx < size - 1 )
          idx_next = idx + 1;
        else
          idx_next = 0;
      end
    end
  end

  //======================================================================
  // Line Tracing
  //======================================================================

  `ifndef SYNTHESIS

  vc_XcelReqMsgTrace xcel_reqstream_msg_trace
  (
    .clk (clk),
    .reset (reset),
    .val   (xcel_reqstream_val),
    .rdy   (xcel_reqstream_rdy),
    .msg   (xcel_reqstream_msg)
  );

  vc_XcelRespMsgTrace xcel_respstream_msg_trace
  (
    .clk (clk),
    .reset (reset),
    .val   (xcel_respstream_val),
    .rdy   (xcel_respstream_rdy),
    .msg   (xcel_respstream_msg)
  );

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin
    xcel_reqstream_msg_trace.line_trace( trace_str );

    vc_trace.append_str( trace_str, "(" );

    case ( state_reg )
      STATE_XCFG:      vc_trace.append_str( trace_str, "X " );
      STATE_M_RD:      vc_trace.append_str( trace_str, "RD" );
      STATE_ADD :      vc_trace.append_str( trace_str, "+ " );
      STATE_M_WR:      vc_trace.append_str( trace_str, "WR" );
      STATE_WAIT:      vc_trace.append_str( trace_str, "W " );
      default:         vc_trace.append_str( trace_str, "? " );
    endcase
    vc_trace.append_str( trace_str, " " );

    if ( state_reg == STATE_ADD ) begin

      $sformat( str, "%x", num_src0 );
      vc_trace.append_str( trace_str, str );
      vc_trace.append_str( trace_str, " " );

      $sformat( str, "%x", num_src1 );
      vc_trace.append_str( trace_str, str );
      vc_trace.append_str( trace_str, " " );

      $sformat( str, "%x", sum_val_next  );
      vc_trace.append_str( trace_str, str );
      vc_trace.append_str( trace_str, " " );

    end
    else begin
      vc_trace.append_chars( trace_str, " ", 27 );
    end

    $sformat( str, "%x", idx[7:0] );
    vc_trace.append_str( trace_str, str );

    vc_trace.append_str( trace_str, "|" );

    $sformat( str, "%x", mem_respstream_msg.data[31:0] );
    vc_trace.append_val_rdy_str( trace_str, mem_respstream_val, mem_respstream_rdy, str );

    vc_trace.append_str( trace_str, ")" );

    xcel_respstream_msg_trace.line_trace( trace_str );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* TUT9_XCEL_VVADD_XCEL_V */

