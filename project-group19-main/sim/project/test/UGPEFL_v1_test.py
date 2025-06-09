#=========================================================================
# UGPEFL_test
#=========================================================================

import pytest
from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL
import random
from random import randint
from project.UGPEFL_v1 import UGPEFL_v1
Bits128 = mk_bits(128)
Bits32 = mk_bits(32)
Bits16 = mk_bits(16)
Bits8 = mk_bits(8)
from project.UGPEFL_v1 import ungapped_extend
from project.UGPEFL_v1 import unpack_data
from project.SeqReadFL_v1 import slice_seq

random.seed(0xdeadbeef)
#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, ugpe ):
    s.src  = StreamSourceFL( Bits128 )
    s.sink = StreamSinkFL  ( Bits32 )
    s.ugpe = ugpe

    s.src.ostream  //= s.ugpe.istream
    s.ugpe.ostream //= s.sink.istream

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + " > " + s.ugpe.line_trace() + " > " + s.sink.line_trace()


#-------------------------------------------------------------------------
# mk_imsg/mk_omsg
#-------------------------------------------------------------------------

def mk_imsg( query, database, q_start, d_start, hit_pos, seq_len ):
  return concat(
    Bits16(seq_len, trunc_int=True), Bits16(hit_pos, trunc_int=True), Bits16(d_start, trunc_int=True),
    Bits16(q_start, trunc_int=True), Bits32(database, trunc_int=True), Bits32(query, trunc_int=True)
  )

def mk_omsg( score, length, q_start, d_start ):
  return concat(
    Bits8( d_start, trunc_int=True ),
    Bits8( q_start, trunc_int=True ),
    Bits8( length, trunc_int=True ),
    Bits8( score, trunc_int=True )
  )

#-------------------------------------------------------------------------
# Test Messages
#-------------------------------------------------------------------------

# basic 
basic_tests = [
  mk_imsg( 0x191C11A, 0x191C11A, 8, 6, 6, 14 ),
  mk_omsg( 14, 14, 2, 0 ),

]


# all match
multi_match_cases = [
  mk_imsg( 0x191C11, 0x191C11, 10, 6, 6, 12 ),
  mk_omsg( 12, 12, 4, 0 ),

  mk_imsg( 0x191C11AA, 0x191C11AA, 6, 6, 6, 16 ),
  mk_omsg( 16, 16, 0, 0 ),

  mk_imsg( 0x191C11E, 0x191C11F, 6, 6, 6, 16 ),
  mk_omsg( 12, 16, 0, 0 ),


]

# all mismatch
multi_mismatch = [
  mk_imsg( 0x00000000, 0xFFFFFFFF, 8, 8, 8, 16 ),
  mk_omsg( 0, 0, 8, 8 ),

  mk_imsg( 0x000000, 0xFFFFFF, 8, 4, 4, 12 ),
  mk_omsg( 0, 0, 8, 4 ),

  mk_imsg( 0x0000, 0xFFFFFF, 10, 2, 2, 8 ),
  mk_omsg( 0, 0, 10, 2 ),
]

 # Hit at boundary
hit_at_boundary = [
  mk_imsg(0x1, 0x2, 15, 1, 1, 2),
  mk_omsg(0, 0, 15, 1),

  mk_imsg(0x1, 0x1, 15, 1, 1, 2),
  mk_omsg(2, 2, 14, 0),

]



# random
random_tests = []

for i in range(1000):  

  query = randint(0, 0xFFFFFFFF)
  database = randint(0, 0xFFFFFFFF)
  q_start = randint(1,15)
  d_start = randint(1,15)

  query_out_slice, database_out_slice, q_start_out_slice, d_start_out_slice, hit_pos, seq_len = slice_seq(
    query, database, q_start, d_start)

  query_unpacked    = unpack_data(query_out_slice)
  database_unpacked = unpack_data(database_out_slice)


  # Call software reference model
  score, length, q_start_out, d_start_out = ungapped_extend(
      query_unpacked, database_unpacked,
      q_start_out_slice, d_start_out_slice, hit_pos, seq_len
  )

  random_tests.append(
    mk_imsg(query_out_slice, database_out_slice, q_start_out_slice, d_start_out_slice, hit_pos, seq_len)
  )
  random_tests.append(
    mk_omsg(score, length, q_start_out, d_start_out) 
  )



#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([ 
  (                           "msgs           src_delay   sink_delay" ),
  [ "basic",                basic_tests,        0,         0        ],
  [ "multi_match",          multi_match_cases,  0,         0        ],
  [ "multi_mismatch",       multi_mismatch,     0,         0        ],
  [ "hit_at_boundary",      hit_at_boundary,    0,         0        ],
  [ "random",               random_tests,       0,         0        ],

  [ "basic_delay",          basic_tests,        3,         3        ],
  [ "multi_match_delay",    multi_match_cases,  3,         3        ],
  [ "multi_mismatch_delay", multi_mismatch,     3,         3        ],
  [ "hit_at_boundary_delay",hit_at_boundary,    3,         3        ],
  [ "random_delay",         random_tests,       3,         3        ],


])

#-------------------------------------------------------------------------
# Test Runner
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params ):

  th = TestHarness(UGPEFL_v1())

  th.set_param( "top.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay+3,
    interval_delay=test_params.src_delay )

  th.set_param( "top.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay+3,
    interval_delay=test_params.sink_delay )

  run_sim( th )
