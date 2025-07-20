#=========================================================================
# SRAMMinion.py
#=========================================================================

from pymtl3 import *
from pymtl3.passes.backends.verilog import *

from pymtl3.stdlib.mem import mk_mem_msg
from pymtl3.stdlib.mem.ifcs import MemResponderIfc

class SRAMMinion( VerilogPlaceholder, Component ):

  def construct( s ):

    MemReqMsg, MemRespMsg = mk_mem_msg( 8, 32, 32 )

    s.minion = MemResponderIfc( MemReqMsg, MemRespMsg )

