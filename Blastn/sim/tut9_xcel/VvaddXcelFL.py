#=========================================================================
# Vector-vector Add Xcel Unit FL Model
#=========================================================================
# Adds two vectors in memory together and stores result in memory.
# Accelerator register interface:
#
#  xr0 : go/done
#  xr1 : base address of the array src0
#  xr2 : base address of the array src1
#  xr3 : base address of the array dest
#  xr4 : size of the array
#
# Accelerator protocol involves the following steps:
#  1. Write the base address of src0 to xr1
#  2. Write the base address of src1 to xr2
#  3. Write the base address of dest to xr3
#  4. Write the number of elements in the array to xr4
#  5. Tell accelerator to go by writing xr0
#  6. Wait for accelerator to finish by reading xr0, result will be 1

from pymtl3 import *
from pymtl3.stdlib.mem.ifcs  import MemRequesterIfc
from pymtl3.stdlib.mem       import MemMsgType, mk_mem_msg
from pymtl3.stdlib.mem       import MemRequesterAdapterFL
from pymtl3.stdlib.xcel.ifcs import XcelResponderIfc
from pymtl3.stdlib.xcel      import XcelMsgType, mk_xcel_msg
from pymtl3.stdlib.stream    import OStreamBlockingAdapterFL
from pymtl3.stdlib.stream    import IStreamBlockingAdapterFL

class VvaddXcelFL( Component ):

  # Constructor

  def construct( s ):

    MemReqMsg16B, MemRespMsg16B = mk_mem_msg( 8, 32, 128 )
    XcelReqMsg,   XcelRespMsg   = mk_xcel_msg( 5, 32 )

    # Interface

    s.xcel = XcelResponderIfc( XcelReqMsg, XcelRespMsg )
    s.mem  = MemRequesterIfc( MemReqMsg16B, MemRespMsg16B )

    # Proc <-> Xcel Adapters

    s.xcelreq_q  = IStreamBlockingAdapterFL( XcelReqMsg  )
    s.xcelresp_q = OStreamBlockingAdapterFL( XcelRespMsg )

    connect( s.xcelreq_q.istream,  s.xcel.reqstream  )
    connect( s.xcelresp_q.ostream, s.xcel.respstream )

    # Xcel <-> Memory Adapters

    s.mem_adapter = MemRequesterAdapterFL( MemReqMsg16B, MemRespMsg16B )

    connect( s.mem, s.mem_adapter.requester )

    # Storage

    s.base_addr_src0 = 0
    s.base_addr_src1 = 0
    s.base_addr_dest = 0
    s.array_size     = 0

    @update_once
    def up_vvadd_xcel():

      # We loop handling accelerator requests. We are only expecting
      # writes to xr0-4, so any other requests are an error. We exit the
      # loop when we see the write to xr0.

      go = False
      while not go:

        xcelreq_msg = s.xcelreq_q.deq()

        if xcelreq_msg.type_ == XcelMsgType.WRITE:
          assert xcelreq_msg.addr in [0,1,2,3,4], \
            "Only reg writes to 0,1,2,3,4 allowed during setup!"

          # Use xcel register address to configure accelerator

          if   xcelreq_msg.addr == 0: go = True
          if   xcelreq_msg.addr == 1: s.base_addr_src0 = xcelreq_msg.data
          elif xcelreq_msg.addr == 2: s.base_addr_src1 = xcelreq_msg.data
          elif xcelreq_msg.addr == 3: s.base_addr_dest = xcelreq_msg.data
          elif xcelreq_msg.addr == 4: s.array_size     = xcelreq_msg.data

          # Send xcel response message

          s.xcelresp_q.enq( XcelRespMsg( XcelMsgType.WRITE, 0 ) )

      for i in range(s.array_size):
        a = s.mem_adapter.read( s.base_addr_src0 + i*4, 4 )
        b = s.mem_adapter.read( s.base_addr_src1 + i*4, 4 )
        s.mem_adapter.write( s.base_addr_dest + i*4, 4, a+b )

      # Now wait for read of xr0

      xcelreq_msg = s.xcelreq_q.deq()

      # Only expecting read from xr0, so any other request is an xcel
      # protocol error.

      assert xcelreq_msg.type_ == XcelMsgType.READ, \
        "Only reg reads allowed during done phase!"

      assert xcelreq_msg.addr == 0, \
        "Only reg read to 0 allowed during done phase!"

      # Send xcel response message indicating xcel is done

      s.xcelresp_q.enq( XcelRespMsg( XcelMsgType.READ, 1 ) )

  # Line tracing

  def line_trace( s ):
    return f"{s.xcel.reqstream}(){s.xcel.respstream}"

