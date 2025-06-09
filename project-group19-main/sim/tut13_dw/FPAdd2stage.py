#=========================================================================
# FPAdd2stage
#=========================================================================

from pymtl3 import *
from pymtl3.passes.backends.verilog import *

class FPAdd2stage( VerilogPlaceholder, Component ):
  def construct( s ):

    s.in_val  = InPort()
    s.in0     = InPort (32)
    s.in1     = InPort (32)

    s.out_val = OutPort()
    s.out     = OutPort(32)

