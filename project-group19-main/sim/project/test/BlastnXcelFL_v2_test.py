#=========================================================================
# BlastnXcelFL_test
#=========================================================================

import pytest
import random
import struct

random.seed(0xdeadbeef)

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream     import StreamSourceFL, StreamSinkFL
from pymtl3.stdlib.mem       import MemMsgType
from pymtl3.stdlib.mem        import MemoryFL, mk_mem_msg
from pymtl3.stdlib.xcel       import XcelMsgType, mk_xcel_msg

from project.BlastnXcelFL_v2 import BlastnXcelFL_v2
from project.BlastnXcelFL_v2 import blastn_xcel
XcelReqMsg, XcelRespMsg = mk_xcel_msg( 5, 32 )

def pack_dna_array(arr):
  return sum((val & 0x3) << (2*i) for i, val in enumerate(arr))

def unpack_dna_word(word):
  return [ (word >> (2*i)) & 0x3 for i in range(16) ]


#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, xcel ):

    s.src  = StreamSourceFL( XcelReqMsg )
    s.sink = StreamSinkFL( XcelRespMsg )
    s.xcel = xcel
    s.mem  = MemoryFL(1, mem_ifc_dtypes=[mk_mem_msg(8,32,32)] )

    s.src.ostream  //= s.xcel.xcel.reqstream
    s.sink.istream //= s.xcel.xcel.respstream
    s.mem.ifc[0]   //= s.xcel.mem

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace()  + " > " + \
           s.xcel.line_trace() + " > " + \
           s.sink.line_trace() + " | " + \
           s.mem.line_trace()

#-------------------------------------------------------------------------
# make messages
#-------------------------------------------------------------------------

def xreq( type_, raddr, data ):
  if type_ == 'rd':
    return XcelReqMsg( XcelMsgType.READ, raddr, data )
  else:
    return XcelReqMsg( XcelMsgType.WRITE, raddr, data )

def xresp( type_, data ):
  if type_ == 'rd':
    return XcelRespMsg( XcelMsgType.READ, data )
  else:
    return XcelRespMsg( XcelMsgType.WRITE, data )

#-------------------------------------------------------------------------
# Xcel Protocol
#-------------------------------------------------------------------------
# These are the source sink messages we need to configure the accelerator
# and wait for it to finish. We use the same messages in all of our
# tests. The difference between the tests is the data to be sorted in the
# test memory.

def gen_xcel_protocol_msgs(query, db_addr, q_start, d_start,
                           score_addr, len_addr, q_start_addr, d_start_addr):

  return [
    xreq('wr', 1, query),         xresp('wr', 0),
    xreq('wr', 2, db_addr),       xresp('wr', 0),
    xreq('wr', 3, q_start),       xresp('wr', 0),
    xreq('wr', 4, d_start),       xresp('wr', 0),
    xreq('wr', 5, score_addr),    xresp('wr', 0),
    xreq('wr', 6, len_addr),      xresp('wr', 0),
    xreq('wr', 7, q_start_addr),  xresp('wr', 0),
    xreq('wr', 8, d_start_addr),  xresp('wr', 0),
    xreq('wr', 0, 0),             xresp('wr', 0),
    xreq('rd', 0, 0),             xresp('rd', 1),
  ]


#-------------------------------------------------------------------------
# Test Cases
#-------------------------------------------------------------------------
basic_test          = [ 0xAAAAAAAA, 0xAAAAAAAA,    4,         4 ]

# full random
full_random = [
  random.randint(0,0xffffffff), 
  random.randint(0,0xffffffff),
  random.randint(1,15),
  random.randint(1,15)
  ]

# part match from start
part_mid_match_from_start = [
  random.randint(0,0xffffffff) & 0xFFF00FFF, 
  random.randint(0,0xffffffff) & 0xFFF00FFF,
  random.randint(1,2),
  random.randint(1,2)
  ]

# part match from mid
part_mid_match_from_mid = [
  random.randint(0,0xffffffff) & 0xFFF00FFF, 
  random.randint(0,0xffffffff) & 0xFFF00FFF,
  random.randint(7,8),
  random.randint(7,8)
  ]

# part match from mid
part_mid_match_from_end = [
  random.randint(0,0xffffffff) & 0xFFF00FFF, 
  random.randint(0,0xffffffff) & 0xFFF00FFF,
  random.randint(14,15),
  random.randint(14,15)
  ]

# part match from start
part_start_match_from_start = [
  random.randint(0,0xffffffff) & 0x000FFFFF, 
  random.randint(0,0xffffffff) & 0x000FFFFF,
  random.randint(1,2),
  random.randint(1,2)
  ]

# part match from mid
part_start_match_from_mid = [
  random.randint(0,0xffffffff) & 0x000FFFFF, 
  random.randint(0,0xffffffff) & 0x000FFFFF,
  random.randint(7,8),
  random.randint(7,8)
  ]

# part match from end
part_start_match_from_end = [
  random.randint(0,0xffffffff) & 0x000FFFFF, 
  random.randint(0,0xffffffff) & 0x000FFFFF,
  random.randint(14,15),
  random.randint(14,15)
  ]

# all mismatch at start
all_mismatch_start = [
  pack_dna_array([0]*16),
  pack_dna_array([3]*16),
  random.randint(1,3),
  random.randint(1,3)
]

# all_mismatch at middle
all_mismatch_mid = [
  pack_dna_array([0]*16),
  pack_dna_array([3]*16),
  random.randint(7,9),
  random.randint(7,9)
]


# all_mismatch at edge
all_mismatch_edge = [
  pack_dna_array([0]*16),
  pack_dna_array([3]*16),
  random.randint(14,15),
  random.randint(1,2)
]

# all_match at start
all_match_start = [
  pack_dna_array([0]*16),
  pack_dna_array([0]*16),
  random.randint(1,3),
  random.randint(1,3)
]

# all_match at middle
all_match_mid = [
  pack_dna_array([0]*16),
  pack_dna_array([0]*16),
  random.randint(7,9),
  random.randint(7,9)
]

# all_match at opp edge
all_match_edge = [
  pack_dna_array([0]*16),
  pack_dna_array([0]*16),
  random.randint(1,2),
  random.randint(14,15)
]

# basic_test          = [ 0xAAAAAAAA, 0xAAAAAAAA,    4,         4 ]
# random_small = [random.randint(0,0xffff), random.randint(0,0xffff),random.randint(1,15),random.randint(1,15)]
# random_large = [random.randint(0,0xffffffff), random.randint(0,0xffffffff),random.randint(1,15),random.randint(1,15)]
#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

# test_case_table = mk_test_case_table([
#   (                 "msgs",           "src_delay", "sink_delay", "stall", "lat" ),
#   [ "basic",        basic_test,           0,          0,            0,         0 ],
#   [ "random_small", random_small,         0,          0 ,            0,         0 ],
#   [ "random_large", random_large,         0,          0 ,            0,         0 ],

#   [ "basic_delay",        basic_test,           3,          3 ,            0.5,         3 ],
#   [ "random_small_delay", random_small,         3,          3 ,            0.5,         3 ],
#   [ "random_large_delay", random_large,         3,          3 ,            0.5,         3 ],

# ])

test_case_table = mk_test_case_table([
  (                                          "msgs",                          "src_delay", "sink_delay" , "stall", "lat" ),
  [ "basic",                              basic_test,                             0,          0,            0,       0 ],
  [ "full_random",                        full_random,                            0,          0,            0,       0 ],

  [ "part_mid_match_from_start",          part_mid_match_from_start,              0,          0,            0,       0 ],
  [ "part_mid_match_from_mid",            part_mid_match_from_mid,                0,          0,            0,       0 ],
  [ "part_mid_match_from_end",            part_mid_match_from_end,                0,          0,            0,       0 ],

  [ "part_start_match_from_start",        part_start_match_from_start,            0,          0,            0,       0 ],
  [ "part_start_match_from_mid",          part_start_match_from_mid,              0,          0,            0,       0 ],
  [ "part_start_match_from_end",          part_start_match_from_end,              0,          0,            0,       0 ],

  [ "all_mismatch_start",                 all_mismatch_start,                     0,          0,            0,       0 ],
  [ "all_mismatch_mid",                   all_mismatch_mid,                       0,          0,            0,       0 ],
  [ "all_mismatch_edge",                  all_mismatch_edge,                      0,          0,            0,       0 ],

  [ "all_match_start",                    all_match_start,                        0,          0,            0,       0 ],
  [ "all_match_mid",                      all_match_mid,                          0,          0,            0,       0 ],
  [ "all_match_edge",                     all_match_edge,                         0,          0,          0.5,     3 ],

  [ "basic_delay",                        basic_test,                             3,          3,          0.5,     3 ],
  [ "full_random_delay",                  full_random,                            3,          3,          0.5,     3 ],

  [ "part_mid_match_from_start_delay",    part_mid_match_from_start,              3,          3,          0.5,     3 ],
  [ "part_mid_match_from_mid_delay",      part_mid_match_from_mid,                3,          3,          0.5,     3 ],
    [ "part_mid_match_from_end_delay",    part_mid_match_from_end,                3,          3,          0.5,     3 ],

  [ "part_start_match_from_start_delay",  part_start_match_from_start,            3,          3,          0.5,     3 ],
  [ "part_start_match_from_mid_delay",    part_start_match_from_mid,              3,          3,          0.5,     3 ],
  [ "part_start_match_from_end_delay",    part_start_match_from_end,              3,          3,          0.5,     3 ],

  [ "all_mismatch_start_delay",           all_mismatch_start,                     3,          3,          0.5,     3 ],
  [ "all_mismatch_mid_delay",             all_mismatch_mid,                       3,          3,          0.5,     3 ],
  [ "all_mismatch_edge_delay",            all_mismatch_edge,                      3,          3,          0.5,     3 ],

  [ "all_match_start_delay",              all_match_start,                        3,          3,          0.5,     3 ],
  [ "all_match_mid_delay",                all_match_mid,                          3,          3,          0.5,     3 ],
  [ "all_match_edge_delay",               all_match_edge,                         3,          3,          0.5,     3 ],

])


#-------------------------------------------------------------------------
# run_test
#-------------------------------------------------------------------------

def run_test( xcel, cmdline_opts, test_params ):

  th = TestHarness( xcel )

  query_word = test_params.msgs[0]
  db_word    = test_params.msgs[1]
  q_start    = test_params.msgs[2]
  d_start    = test_params.msgs[3]

  db_addr = 0x1000
  db_bytes = struct.pack("<I", db_word)


  query_arr    = [ (query_word >> (2*i)) & 0x3 for i in range(16) ]
  database_arr = [ (db_word >> (2*i)) & 0x3 for i in range(16) ]


  score_exp, length_exp, q_start_exp, d_start_exp = blastn_xcel(
      query_arr, database_arr, q_start, d_start
  )

  score_addr    = 0x200
  len_addr      = 0x204
  q_start_addr  = 0x208
  d_start_addr  = 0x20C

  xcel_protocol_msgs = gen_xcel_protocol_msgs(
    test_params.msgs[0], db_addr,
    test_params.msgs[2], test_params.msgs[3],
    score_addr, len_addr, q_start_addr, d_start_addr
  )
  xreqs  = xcel_protocol_msgs[::2]
  xresps = xcel_protocol_msgs[1::2]

  th.set_param( "top.src.construct", msgs=xcel_protocol_msgs[::2],
    initial_delay=test_params.src_delay+3, interval_delay=test_params.src_delay )

  th.set_param( "top.sink.construct", msgs=xcel_protocol_msgs[1::2],
    initial_delay=test_params.sink_delay+3, interval_delay=test_params.sink_delay )
  
  th.set_param( "top.mem.construct",
    stall_prob=test_params.stall, extra_latency=test_params.lat )


  th.elaborate()
  th.mem.write_mem(db_addr, db_bytes)

  if cmdline_opts is not None:
    if cmdline_opts['max_cycles'] is None:
      cmdline_opts['max_cycles'] = 20000


  run_sim( th, cmdline_opts, duts=['xcel'] )

  for msg in th.sink.msgs:
    if msg.type_ == MemMsgType.WRITE:
      result_bytes = th.mem.read_mem(score_addr, 16)
      score_out, length_out, q_start_out, d_start_out = struct.unpack("<4I", result_bytes)
      # d_start_out, q_start_out, length_out, score_out= struct.unpack("<4I", result_bytes)
      print(f"score={score_out} len={length_out} q_start={q_start_out} d_start={d_start_out}")

  # # Read result values from memory after simulation
  # result_bytes = th.mem.read_mem(score_addr, 16)
  # score_out, length_out, q_start_out, d_start_out = struct.unpack("<4I", result_bytes)

  # Compare against expected values
  assert score_out     == score_exp,     f"Score mismatch!     Got {score_out}, expected {score_exp}"
  assert length_out    == length_exp,    f"Length mismatch!    Got {length_out}, expected {length_exp}"
  assert q_start_out   == q_start_exp,   f"Q_start mismatch!   Got {q_start_out}, expected {q_start_exp}"
  assert d_start_out   == d_start_exp,   f"D_start mismatch!   Got {d_start_out}, expected {d_start_exp}"




#-------------------------------------------------------------------------
# run_test_multiple
#-------------------------------------------------------------------------
def run_test_multiple( xcel, cmdline_opts ):

  random.seed(0xdeadbeef)

  query_dbs = []
  all_msgs = []
  expected_results = []
  db_addr_base = 0x1000
  output_base  = 0x200

  for i in range(8):
    query_word = random.randint(0, 0xFFFFFFFF)
    db_word    = random.randint(0, 0xFFFFFFFF)
    q_start    = random.randint(1, 14)
    d_start    = random.randint(1, 14)

    query_arr    = [ (query_word >> (2*j)) & 0x3 for j in range(16) ]
    database_arr = [ (db_word >> (2*j)) & 0x3 for j in range(16) ]

    score_exp, length_exp, q_start_exp, d_start_exp = blastn_xcel(
      query_arr, database_arr, q_start, d_start
    )

    db_addr = db_addr_base + i*4
    score_addr    = output_base + i*16 + 0x0
    len_addr      = output_base + i*16 + 0x4
    q_start_addr  = output_base + i*16 + 0x8
    d_start_addr  = output_base + i*16 + 0xC

    query_dbs.append((db_addr, db_word))
    all_msgs.extend( gen_xcel_protocol_msgs(
      query_word, db_addr, q_start, d_start,
      score_addr, len_addr, q_start_addr, d_start_addr
    ))

    expected_results.append((score_exp, length_exp, q_start_exp, d_start_exp))

  th = TestHarness( xcel )
  th.set_param("top.src.construct",  msgs=all_msgs[::2], initial_delay=3, interval_delay=3)
  th.set_param("top.sink.construct", msgs=all_msgs[1::2], initial_delay=3, interval_delay=3)
  th.set_param("top.mem.construct", stall_prob=0.5, extra_latency=3)
  th.elaborate()

  for addr, db_word in query_dbs:
    db_bytes = struct.pack("<I", db_word)
    th.mem.write_mem(addr, db_bytes)

  if cmdline_opts.get('max_cycles') is None:
    cmdline_opts['max_cycles'] = 200000

  run_sim(th, cmdline_opts, duts=['xcel'])

  for i in range(16):
    base = output_base + i*16
    result_bytes = th.mem.read_mem(base, 16)
    score_out, length_out, q_start_out, d_start_out = struct.unpack("<4I", result_bytes)
    score_exp, length_exp, q_start_exp, d_start_exp = expected_results[i]

    assert score_out     == score_exp,     f"[{i}] Score mismatch! Got {score_out}, expected {score_exp}"
    assert length_out    == length_exp,    f"[{i}] Length mismatch! Got {length_out}, expected {length_exp}"
    assert q_start_out   == q_start_exp,   f"[{i}] Q_start mismatch! Got {q_start_out}, expected {q_start_exp}"
    assert d_start_out   == d_start_exp,   f"[{i}] D_start mismatch! Got {d_start_out}, expected {d_start_exp}"

#-------------------------------------------------------------------------
# Test Cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test_blastn_xcel_fl( cmdline_opts, test_params ):
  run_test( BlastnXcelFL_v2(), cmdline_opts, test_params )

# def test_multiple( cmdline_opts ):
#   run_test_multiple( BlastnXcelFL_v2(), cmdline_opts )