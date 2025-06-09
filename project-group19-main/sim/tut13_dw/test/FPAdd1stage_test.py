#=========================================================================
# FPUAdd1stage_test
#=========================================================================

from pymtl3 import *
from pymtl3.stdlib.test_utils import run_test_vector_sim

from struct import pack
from tut13_dw.FPAdd1stage import FPAdd1stage

#-------------------------------------------------------------------------
# fp2bits
#-------------------------------------------------------------------------

def fp2bits( fp ):
  if fp == '?':
    return '?'
  else:
    return Bits32(int.from_bytes( pack( '>f', fp ), byteorder='big' ))

def row( in_val, in0, in1, out_val, out ):
  return [ in_val, fp2bits(in0), fp2bits(in1), out_val, fp2bits(out) ]

#-------------------------------------------------------------------------
# test_basic
#-------------------------------------------------------------------------

def test_basic( cmdline_opts ):
  run_test_vector_sim( FPAdd1stage(), [
       ( 'in_val in0   in1   out_val* out*'   ),
    row( 0,      0.00, 0.00, 0,       '?'     ),
    row( 1,      1.00, 1.00, 0,       '?'     ),
    row( 1,      1.50, 1.50, 1,       2.00    ),
    row( 1,      1.25, 2.50, 1,       3.00    ),
    row( 0,      0.00, 0.00, 1,       3.75    ),
    row( 0,      0.00, 0.00, 0,       '?'     ),
  ], cmdline_opts )

