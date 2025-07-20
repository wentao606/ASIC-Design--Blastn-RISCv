#=========================================================================
# Blastn Xcel Unit PyMTL Wrapper
#=========================================================================

from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.mem.ifcs  import MemRequesterIfc
from pymtl3.stdlib.mem       import mk_mem_msg
from pymtl3.stdlib.xcel.ifcs import XcelResponderIfc
from pymtl3.stdlib.xcel      import mk_xcel_msg

class BlastnXcel_v1( VerilogPlaceholder, Component ):

  def construct( s ):

    XcelReqMsg, XcelRespMsg = mk_xcel_msg( 5, 32 )
    XcelReqMsg, XcelRespMsg = mk_xcel_msg( 5, 32 )
    MemReqMsg,  MemRespMsg  = mk_mem_msg( 8, 32, 32 )

    s.xcel = XcelResponderIfc( XcelReqMsg, XcelRespMsg )
    s.mem  = MemRequesterIfc( MemReqMsg, MemRespMsg )

    s.set_metadata( VerilogTranslationPass.explicit_module_name,
                    'BlastnXcel_v1' )

