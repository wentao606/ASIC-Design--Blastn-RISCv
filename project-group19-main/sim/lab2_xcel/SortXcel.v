//=========================================================================
// Sorting Accelerator Implementation
//=========================================================================
// Sort array in memory containing positive integers.
// Accelerator register interface:
//
//  xr0 : go/done
//  xr1 : base address of array
//  xr2 : number of elements in array
//
// Accelerator protocol involves the following steps:
//  1. Write the base address of array via xr1
//  2. Write the number of elements in array via xr2
//  3. Tell accelerator to go by writing xr0
//  4. Wait for accelerator to finish by reading xr0, result will be 1
//

`ifndef LAB2_SORT_SORT_XCEL_V
`define LAB2_SORT_SORT_XCEL_V

`include "vc/trace.v"

`include "vc/mem-msgs.v"
`include "vc/xcel-msgs.v"
`include "vc/queues.v"

//=========================================================================
// Sorting Accelerator Implementation
//=========================================================================

module lab2_xcel_SortXcel
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

  // ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Create RTL model for sorting xcel
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

  // This bypass queue is to cut the ready path

  logic         memreq_enq_val;
  logic         memreq_enq_rdy;
  mem_req_16B_t memreq_enq_msg;

  vc_Queue#(`VC_QUEUE_BYPASS,$bits(mem_req_16B_t),1) memreq_q
  (
    .clk     (clk),
    .reset   (reset),
    .num_free_entries(),

    .enq_val (memreq_enq_val),
    .enq_rdy (memreq_enq_rdy),
    .enq_msg (memreq_enq_msg),

    .deq_val (mem_reqstream_val),
    .deq_rdy (mem_reqstream_rdy),
    .deq_msg (mem_reqstream_msg_raw)
  );

  // Extra state registers

  logic [31:0] base_addr,   base_addr_next;
  logic [31:0] size,        size_next;
  logic [31:0] inner_count, inner_count_next;
  logic [31:0] outer_count, outer_count_next;
  logic [31:0] a,           a_next;

  always_ff @(posedge clk) begin
    if (reset) begin
      outer_count <= 0;
      inner_count <= 0;
      base_addr   <= 0;
      size        <= 0;
      a           <= 0;
    end
    else begin
      outer_count <= outer_count_next;
      inner_count <= inner_count_next;
      base_addr   <= base_addr_next;
      size        <= size_next;
      a           <= a_next;
    end
  end

  //======================================================================
  // State Update
  //======================================================================

  localparam STATE_XCFG    = 3'd0;
  localparam STATE_FIRST0  = 3'd1;
  localparam STATE_FIRST1  = 3'd2;
  localparam STATE_BUBBLE0 = 3'd3;
  localparam STATE_BUBBLE1 = 3'd4;
  localparam STATE_LAST    = 3'd5;

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
            state_reg <= STATE_FIRST0;

        STATE_FIRST0:
          if ( memreq_enq_rdy )
            state_reg <= STATE_FIRST1;

        STATE_FIRST1:
          if ( memreq_enq_rdy && memresp_deq_val )
            state_reg <= STATE_BUBBLE0;

        STATE_BUBBLE0:
          if ( memreq_enq_rdy && memresp_deq_val )
            state_reg <= STATE_BUBBLE1;

        STATE_BUBBLE1:
          if ( memreq_enq_rdy && memresp_deq_val )
            if ( inner_count+1 < size )
              state_reg <= STATE_BUBBLE0;
            else
              state_reg <= STATE_LAST;

        STATE_LAST:
          if ( memreq_enq_rdy && memresp_deq_val )
            if ( outer_count+1 < size )
              state_reg <= STATE_FIRST1;
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

  always_comb begin

    xcelreq_deq_rdy         = 0;
    xcel_respstream_val     = 0;
    memreq_enq_val          = 0;
    memreq_enq_msg          = 0;
    memresp_deq_rdy         = 0;
    go                      = 0;
    xcel_respstream_msg_raw = 0;

    a_next                  = a;
    outer_count_next        = outer_count;
    inner_count_next        = inner_count;
    base_addr_next          = base_addr;
    size_next               = size;

    //--------------------------------------------------------------------
    // STATE: XCFG
    //--------------------------------------------------------------------

    if ( state_reg == STATE_XCFG ) begin

      if ( xcelreq_deq_val & xcel_respstream_rdy ) begin
        xcelreq_deq_rdy = 1;
      end
      if ( xcelreq_deq_val ) begin
        xcel_respstream_val     = 1;

        // Send xcel response message, obviously you only want to
        // send the response message when accelerator is done

        if ( xcelreq_deq_msg.type_ == `VC_XCEL_REQ_MSG_TYPE_READ ) begin
          xcel_respstream_msg_raw.type_ = `VC_XCEL_REQ_MSG_TYPE_READ;
          xcel_respstream_msg_raw.data  = 1;
        end
        else begin
          if ( xcelreq_deq_msg.addr == 0 ) begin
            outer_count_next = 0;
            inner_count_next = 0;
            go               = 1;
          end
          else if ( xcelreq_deq_msg.addr == 1 )
            base_addr_next = xcelreq_deq_msg.data;

          else if ( xcelreq_deq_msg.addr == 2 )
            size_next = xcelreq_deq_msg.data;

          xcel_respstream_msg_raw.type_ = `VC_XCEL_REQ_MSG_TYPE_WRITE;
          xcel_respstream_msg_raw.data  = 0;
        end
      end
    end

    //--------------------------------------------------------------------
    // STATE: FIRST0
    //--------------------------------------------------------------------
    // Send the first memory read request for the very first element in
    // the array.

    else if ( state_reg == STATE_FIRST0 ) begin
      memreq_enq_val = 1;
      memreq_enq_msg.type_ = `VC_MEM_REQ_MSG_TYPE_READ;
      memreq_enq_msg.addr  = base_addr + (inner_count << 2);
      memreq_enq_msg.len   = 4;
      memreq_enq_msg.data  = 0;

      if ( memreq_enq_rdy ) begin
        inner_count_next = 1;
      end
    end

    //--------------------------------------------------------------------
    // STATE: FIRST1
    //--------------------------------------------------------------------
    // Wait for the memory response for the first element in the array,
    // and once it arrives store this element in a, and send the memory
    // read request for the second element.

    else if ( state_reg == STATE_FIRST1 ) begin

      if ( memreq_enq_rdy && memresp_deq_val ) begin
        memresp_deq_rdy = 1;
        memreq_enq_val  = 1;

        a_next = memresp_deq_msg.data;

        memreq_enq_msg.type_ = `VC_MEM_REQ_MSG_TYPE_READ;
        memreq_enq_msg.addr  = base_addr + (inner_count << 2);
        memreq_enq_msg.len   = 4;
        memreq_enq_msg.data  = 0;

      end
    end

    //--------------------------------------------------------------------
    // STATE: BUBBLE0
    //--------------------------------------------------------------------
    // Wait for the memory read response to get the next element, compare
    // the new value to the previous max value, update b with the new max
    // value, and send a memory request to store the new min value.
    // Notice how we decrement the write address by four since we want to
    // store to the new min value _previous_ element.

    else if ( state_reg == STATE_BUBBLE0 ) begin

      if ( memreq_enq_rdy && memresp_deq_val ) begin
        memresp_deq_rdy = 1;
        memreq_enq_val  = 1;

        if ( a > memresp_deq_msg.data ) begin
          a_next = a;
          memreq_enq_msg.data = memresp_deq_msg.data;
        end
        else begin
          a_next = memresp_deq_msg.data;
          memreq_enq_msg.data = a;
        end

        memreq_enq_msg.type_ = `VC_MEM_REQ_MSG_TYPE_WRITE;
        memreq_enq_msg.addr  = base_addr + ((inner_count-1) << 2);
        memreq_enq_msg.len   = 4;

      end
    end

    //--------------------------------------------------------------------
    // STATE: BUBBLE1
    //--------------------------------------------------------------------
    // Wait for the memory write response, and then check to see if we
    // have reached the end of the array. If we have not reached the end
    // of the array, then make a new memory read request for the next
    // element; if we have reached the end of the array, then make a
    // final write request (with value from a) to update the final
    // element in the array.

    else if ( state_reg == STATE_BUBBLE1 ) begin

      if ( memreq_enq_rdy && memresp_deq_val ) begin
        memresp_deq_rdy = 1;
        memreq_enq_val  = 1;

        inner_count_next = inner_count + 1;
        if ( inner_count+1 < size ) begin

          memreq_enq_msg.type_ = `VC_MEM_REQ_MSG_TYPE_READ;
          memreq_enq_msg.addr  = base_addr + ((inner_count+1) << 2);
          memreq_enq_msg.len   = 4;
          memreq_enq_msg.data  = 0;

        end
        else begin

          memreq_enq_msg.type_ = `VC_MEM_REQ_MSG_TYPE_WRITE;
          memreq_enq_msg.addr  = base_addr + (inner_count << 2);
          memreq_enq_msg.len   = 4;
          memreq_enq_msg.data  = a;

        end

      end
    end

    //--------------------------------------------------------------------
    // STATE: LAST
    //--------------------------------------------------------------------
    // Wait for the last response, and then check to see if we need to go
    // through the array again. If we do need to go through array again,
    // then make a new memory read request for the very first element in
    // the array; if we do not need to go through the array again, then
    // we are all done and we can go back to accelerator configuration.

    else if ( state_reg == STATE_LAST ) begin

      if ( memreq_enq_rdy && memresp_deq_val ) begin
        memresp_deq_rdy = 1;

        outer_count_next = outer_count + 1;
        if ( outer_count+1 < size ) begin

          memreq_enq_val       = 1;
          memreq_enq_msg.type_ = `VC_MEM_REQ_MSG_TYPE_READ;
          memreq_enq_msg.addr  = base_addr;
          memreq_enq_msg.len   = 4;
          memreq_enq_msg.data  = 0;

          inner_count_next     = 1;

        end

      end

    end

  end

  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

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

    // ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''
    // Define line trace here
    // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    $sformat( str, "%x", outer_count[11:0] );
    vc_trace.append_str( trace_str, str );
    vc_trace.append_str( trace_str, " " );

    $sformat( str, "%x", inner_count[11:0] );
    vc_trace.append_str( trace_str, str );
    vc_trace.append_str( trace_str, " " );

    case ( state_reg )
      STATE_XCFG:      vc_trace.append_str( trace_str, "X " );
      STATE_FIRST0:    vc_trace.append_str( trace_str, "F0" );
      STATE_FIRST1:    vc_trace.append_str( trace_str, "F1" );
      STATE_BUBBLE0:   vc_trace.append_str( trace_str, "B0" );
      STATE_BUBBLE1:   vc_trace.append_str( trace_str, "B1" );
      STATE_LAST:      vc_trace.append_str( trace_str, "L " );
      default:         vc_trace.append_str( trace_str, "? " );
    endcase

    // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

    vc_trace.append_str( trace_str, ")" );

    xcel_respstream_msg_trace.line_trace( trace_str );
  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* LAB2_XCEL_SORT_XCEL_V */
