#=========================================================================
# DataMemXbar
#=========================================================================

from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.mem.ifcs    import MemRequesterIfc, MemResponderIfc
from pymtl3.stdlib.mem         import mk_mem_msg

class DataMemXbar( VerilogPlaceholder, Component ):
  def construct( s ):

    MemReqMsg4B,  MemRespMsg4B  = mk_mem_msg( 8, 32, 32 )
    MemReqMsg16B, MemRespMsg16B = mk_mem_msg( 8, 32, 128 )

    s.dmem = MemResponderIfc( MemReqMsg4B,  MemRespMsg4B  )
    s.xmem = MemResponderIfc( MemReqMsg16B, MemRespMsg16B )
    s.mem  = MemRequesterIfc( MemReqMsg16B, MemRespMsg16B )

