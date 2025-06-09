#=========================================================================
# UGPE Unit PyMTL Wrapper
#=========================================================================

from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
Bits128 = mk_bits(128)

class SeqRead_v1( VerilogPlaceholder, Component ):
  def construct( s ):
    s.istream = IStreamIfc( Bits128 )
    s.ostream = OStreamIfc( Bits128 )

    s.set_metadata( VerilogTranslationPass.explicit_module_name,
                    'SeqRead_v1' )

