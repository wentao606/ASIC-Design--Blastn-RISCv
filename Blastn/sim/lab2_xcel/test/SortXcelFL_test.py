#=========================================================================
# SortXcelFL_test
#=========================================================================

import pytest
import random
import struct

random.seed(0xdeadbeef)

from pymtl3 import *
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream     import StreamSourceFL, StreamSinkFL
from pymtl3.stdlib.mem        import MemoryFL, mk_mem_msg
from pymtl3.stdlib.xcel       import XcelMsgType, mk_xcel_msg

from lab2_xcel.SortXcelFL import SortXcelFL

XcelReqMsg, XcelRespMsg = mk_xcel_msg( 5, 32 )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, xcel ):

    s.src  = StreamSourceFL( XcelReqMsg )
    s.sink = StreamSinkFL( XcelRespMsg )
    s.xcel = xcel
    s.mem  = MemoryFL(1, mem_ifc_dtypes=[mk_mem_msg(8,32,128)] )

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

def gen_xcel_protocol_msgs( base_addr, size ):
  return [
    xreq( 'wr', 1, base_addr ), xresp( 'wr', 0 ),
    xreq( 'wr', 2, size      ), xresp( 'wr', 0 ),
    xreq( 'wr', 0, 0         ), xresp( 'wr', 0 ),
    xreq( 'rd', 0, 0         ), xresp( 'rd', 1 ),
  ]

#-------------------------------------------------------------------------
# Test Cases
#-------------------------------------------------------------------------

mini          = [ 0x21, 0x14, 0x42, 0x03 ]
small_data    = [ random.randint(0,0xffff)     for i in range(32) ]
large_data    = [ random.randint(0,0x7fffffff) for i in range(32) ]
sort_fwd_data = sorted(small_data)
sort_rev_data = list(reversed(sorted(small_data)))
nonpow2_size  = [ random.randint(0,0xffff)     for i in range(35) ]

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
                         #                delays   test mem
                         #                -------- ---------
  (                      "data            src sink stall lat"),
  [ "mini",               mini,           0,  0,   0,    0   ],
  [ "mini_delay_3x14x2",  mini,           3, 14,   0.5,  2   ],
  [ "mini_delay_5x7x4",   mini,           5,  7,   0.5,  4   ],
  [ "small_data",         small_data,     0,  0,   0,    0   ],
  [ "large_data",         large_data,     0,  0,   0,    0   ],
  [ "sort_fwd_data",      sort_fwd_data,  0,  0,   0,    0   ],
  [ "sort_rev_data",      sort_rev_data,  0,  0,   0,    0   ],
  [ "nonpow2_size",       nonpow2_size,   0,  0,   0,    0   ],
  [ "small_data_3x14x0",  small_data,     3, 14,   0,    0   ],
  [ "small_data_5x7x0",   small_data,     5,  7,   0,    0   ],
  [ "small_data_0x0x4",   small_data,     0,  0,   0.5,  4   ],
  [ "small_data_3x14x4",  small_data,     3,  14,  0.5,  4   ],
  [ "small_data_5x7x4",   small_data,     5,  7,   0.5,  4   ],
])

#-------------------------------------------------------------------------
# run_test
#-------------------------------------------------------------------------

def run_test( xcel, test_params, cmdline_opts=None ):

  # Convert test data into byte array

  data = test_params.data
  data_bytes = struct.pack("<{}I".format(len(data)),*data)

  # Protocol messages

  xcel_protocol_msgs = gen_xcel_protocol_msgs( 0x1000, len(data) )
  xreqs  = xcel_protocol_msgs[::2]
  xresps = xcel_protocol_msgs[1::2]

  # Create test harness with protocol messagse

  th = TestHarness( xcel )

  th.set_param( "top.src.construct", msgs=xcel_protocol_msgs[::2],
    initial_delay=test_params.src+3, interval_delay=test_params.src )

  th.set_param( "top.sink.construct", msgs=xcel_protocol_msgs[1::2],
    initial_delay=test_params.sink+3, interval_delay=test_params.sink )

  th.set_param( "top.mem.construct",
    stall_prob=test_params.stall, extra_latency=test_params.lat )

  th.elaborate()

  # Load the data into the test memory

  th.mem.write_mem( 0x1000, data_bytes )

  # Enlarge max_cycles

  if cmdline_opts is not None:
    if cmdline_opts['max_cycles'] is None:
      cmdline_opts['max_cycles'] = 20000

  # Run the test

  run_sim( th, cmdline_opts, duts=['xcel'] )

  # Retrieve data from test memory

  result_bytes = th.mem.read_mem( 0x1000, len(data_bytes) )

  # Convert result bytes into list of ints

  result = list(struct.unpack("<{}I".format(len(data)),result_bytes))

  # Compare result to sorted reference

  assert result == sorted(data)

#-------------------------------------------------------------------------
# run_test_multiple
#-------------------------------------------------------------------------
# We want to make sure we can use our accelerator multiple times, so we
# create an array of 32 elements and then we use the accelerator to sort
# the first four elements, the second four elements, etc.

def run_test_multiple( xcel, cmdline_opts=None ):

  # Convert test data into byte array

  random.seed(0xdeadbeef)

  data = [ random.randint(0,0xffff) for i in range(32) ]
  data_bytes = struct.pack("<{}I".format(len(data)),*data)

  # Protocol messages

  base_addr = 0x1000
  msgs = []

  for i in range(8):
    msgs.extend( gen_xcel_protocol_msgs( base_addr+i*16, 4 ) )

  # Create test harness with protocol messagse

  th = TestHarness( xcel )

  th.set_param( "top.src.construct", msgs=msgs[::2],
    initial_delay=6, interval_delay=3 )

  th.set_param( "top.sink.construct", msgs=msgs[1::2],
    initial_delay=10, interval_delay=7 )

  th.set_param( "top.mem.construct", stall_prob=0.5, extra_latency=3 )

  th.elaborate()

  # Load the data into the test memory

  th.mem.write_mem( 0x1000, data_bytes )

  # Enlarge max_cycles

  if cmdline_opts is not None:
    if cmdline_opts['max_cycles'] is None:
      cmdline_opts['max_cycles'] = 20000

  # Run the test

  run_sim( th, cmdline_opts, duts=['xcel'] )

  # Retrieve data from test memory

  result_bytes = th.mem.read_mem( 0x1000, len(data_bytes) )

  # Convert result bytes into list of ints

  result = list(struct.unpack("<{}I".format(len(data)),result_bytes))

  # Compare result to sorted reference

  for i in range(8):
    assert result[i*4:i*4+4] == sorted(data[i*4:i*4+4])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params ):
  run_test( SortXcelFL(), test_params )

def test_multiple():
  run_test_multiple( SortXcelFL() )

