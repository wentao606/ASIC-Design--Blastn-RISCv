#=========================================================================
# vvadd_xcel_sim_test
#=========================================================================
# Make sure that vvadd-xcel-sim works.

import pytest
import os

from subprocess import check_call, CalledProcessError
from itertools  import product

impls  = [ "fl", "rtl" ]

inputs = [ "small", "large", "multiple" ]

test_cases = []

for impl in impls:
  for inp in inputs:
    test_cases.append([ impl, inp ])

@pytest.mark.parametrize( "impl,input_", test_cases )
def test( impl, input_, cmdline_opts ):

  # Get path to simulator script

  test_dir = os.path.dirname( os.path.abspath( __file__ ) )
  sim_dir  = os.path.dirname( test_dir )
  sim      = sim_dir + os.path.sep + 'vvadd-xcel-sim'

  # Command

  cmd = [ sim, "--impl", impl, "--input", input_ ]

  # Handle test verilog

  if cmdline_opts['test_verilog']:
    if impl.startswith("rtl"):
      cmd.append( "--translate" )
    else:
      pytest.skip("ignoring non-Verilog tests")

    if cmdline_opts['dump_vtb']:
      cmd.append( "--dump-vtb" )
    if cmdline_opts['dump_vcd']:
      cmd.append( "--dump-vcd" )

  # Display simulator command line

  print("")
  print("Simulator command line:", ' '.join(cmd))

  # Run the simulator

  try:
    check_call(cmd)
  except CalledProcessError as e:
    raise Exception( "Error running simulator!" )

