#=========================================================================
# UGPE Unit PyMTL Wrapper
#=========================================================================

from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
Bits128 = mk_bits(128)
Bits160 = mk_bits(160)

class UGPE_v2( VerilogPlaceholder, Component ):
  def construct( s ):
    s.istream = IStreamIfc( Bits128 )
    s.ostream = OStreamIfc( Bits160 )

    s.set_metadata( VerilogTranslationPass.explicit_module_name,
                    'UGPE_v2' )

