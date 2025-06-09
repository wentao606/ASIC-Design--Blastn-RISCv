#=========================================================================
# SeqReadFL_test
#=========================================================================

import pytest
from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL
import random
from random import randint
from project.SeqReadFL_v1 import SeqReadFL_v1
from project.SeqReadFL_v1 import slice_seq
Bits128 = mk_bits(128)
Bits32  = mk_bits(32)
Bits16  = mk_bits(16)

random.seed(0xdeadbeef)
#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, seqread ):
    s.src  = StreamSourceFL( Bits128 )
    s.sink = StreamSinkFL  ( Bits128 )
    s.seqread = seqread

    s.src.ostream  //= s.seqread.istream
    s.seqread.ostream //= s.sink.istream

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + " > " + s.seqread.line_trace() + " > " + s.sink.line_trace()


#-------------------------------------------------------------------------
# mk_imsg/mk_omsg
#-------------------------------------------------------------------------

def mk_imsg( query, database, q_start, d_start):
  return concat(
    Bits32(d_start, trunc_int=True), Bits32(q_start, trunc_int=True), 
    Bits32(database, trunc_int=True), Bits32(query, trunc_int=True)
  )

def mk_omsg( query_out, database_out, q_start_out, d_start_out, hit_pos, seq_len ):
  return concat(
    Bits16( seq_len, trunc_int=True ),
    Bits16( hit_pos, trunc_int=True ),
    Bits16( d_start_out, trunc_int=True ),
    Bits16( q_start_out, trunc_int=True ),
    Bits32( database_out, trunc_int=True ),
    Bits32( query_out, trunc_int=True )
  )

#-------------------------------------------------------------------------
# Test Messages
#-------------------------------------------------------------------------

# basic 
basic_tests = [
  mk_imsg( 0x191C11A7, 0x4191C11A, 8, 6 ),
  mk_omsg( 0x191C11A, 0x191C11A, 8, 6, 6, 14 ),

  mk_imsg( 0x2109A877, 0x41554267, 8, 4 ),
  mk_omsg( 0x2109A8, 0x554267, 8, 4, 4, 12 ),
]


# all match
multi_match_cases = [
  mk_imsg(0xAAAAAAAA, 0xAAAAAAAA, 8, 8),
  mk_omsg(0xAAAAAAAA, 0xAAAAAAAA, 8, 8, 8, 16),

  mk_imsg(0xA0A0A0A0, 0xB0B0B0B0, 10, 10),
  mk_omsg(0xAA0A0A0A0, 0xB0B0B0B0, 10, 10, 10, 16),
]

 # Hit at boundary
hit_at_boundary = [
  mk_imsg(0xAAAAAAAA, 0xBBBBBBBB, 15, 1),
  mk_omsg(0xA, 0xB, 15, 1, 1, 2),
]



# random
random_tests = []

for i in range(50):  

  query = randint(0, 0xFFFFFFFF)
  database = randint(0, 0xFFFFFFFF)
  q_start = randint(1,15)
  d_start = randint(1,15)

  query_out, database_out, q_start_out, d_start_out, hit_pos, seq_len = slice_seq(query, database, q_start, d_start)


  random_tests.append(
    mk_imsg(query, database, q_start, d_start )
  )
  random_tests.append(
    mk_omsg(query_out, database_out, q_start_out, d_start_out, hit_pos, seq_len)  # placeholder output
  )




#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([ 
  (                           "msgs           src_delay   sink_delay" ),
  [ "basic",                basic_tests,        0,         0        ],
  [ "multi_match",          multi_match_cases,  0,         0        ],
  [ "hit_at_boundary",      hit_at_boundary,    0,         0        ],
  [ "random",               random_tests,       0,         0        ],

  [ "basic_delay",          basic_tests,        3,         3        ],
  [ "multi_match_delay",    multi_match_cases,  3,         3        ],
  [ "hit_at_boundary_delay",hit_at_boundary,   3,         3        ],
  [ "random_delay",         random_tests,       3,         3        ],


])

#-------------------------------------------------------------------------
# Test Runner
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params ):

  th = TestHarness(SeqReadFL_v1())

  th.set_param( "top.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay+3,
    interval_delay=test_params.src_delay )

  th.set_param( "top.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay+3,
    interval_delay=test_params.sink_delay )

  run_sim( th )
