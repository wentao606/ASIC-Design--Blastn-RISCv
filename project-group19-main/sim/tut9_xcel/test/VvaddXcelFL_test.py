#=========================================================================
# VvaddXcelFL_test
#=========================================================================

import pytest
import random
import struct

random.seed(0xdeadbeef)

from pymtl3 import *
from pymtl3.stdlib import stream
from pymtl3.stdlib.test_utils import mk_test_case_table, run_sim
from pymtl3.stdlib.stream     import StreamSourceFL, StreamSinkFL
from pymtl3.stdlib.mem        import MemoryFL, mk_mem_msg
from pymtl3.stdlib.xcel       import XcelMsgType, mk_xcel_msg

from tut9_xcel.VvaddXcelFL  import VvaddXcelFL

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
# tests. The difference between the tests is the data. The variable i is
# used to offset multiple data sets in memory

def gen_xcel_protocol_msgs( size, i ):
  return [
    xreq( 'wr', 1, 0x1000 + 0x3000*i ), xresp( 'wr', 0 ),
    xreq( 'wr', 2, 0x2000 + 0x3000*i ), xresp( 'wr', 0 ),
    xreq( 'wr', 3, 0x3000 + 0x3000*i ), xresp( 'wr', 0 ),
    xreq( 'wr', 4, size              ), xresp( 'wr', 0 ),
    xreq( 'wr', 0, 0                 ), xresp( 'wr', 0 ),
    xreq( 'rd', 0, 0                 ), xresp( 'rd', 1 ),
  ]

#-------------------------------------------------------------------------
# Test Cases
#-------------------------------------------------------------------------

mini          = [ [ 0x1, 0x2, 0x3, 0x4],[ 0x5, 0x6, 0x7, 0x8 ] ]
small_data    = [ [ random.randint(0,0xffff)     for i in range(32) ], \
                  [ random.randint(0,0xffff)     for i in range(32) ] ]
large_data    = [ [ random.randint(0,0x7fffffff) for i in range(32) ], \
                  [ random.randint(0,0x7fffffff) for i in range(32) ] ]
multiple      = [ [ random.randint(0,0x7fffffff) for i in range(32) ] for j in range(8) ]

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
                         #                delays   test mem
                         #                -------- ---------
  (                      "data            src sink stall lat"),
  [ "mini",               mini,           0,  0,   0,    0   ],
  [ "mini_delay_3x14x4",  mini,           3, 14,   0.5,  4   ],
  [ "small_data",         small_data,     0,  0,   0,    0   ],
  [ "large_data",         large_data,     0,  0,   0,    0   ],
  [ "multi_data",         multiple,       0,  0,   0,    0   ],
  [ "small_data_3x14x0",  small_data,     3, 14,   0,    0   ],
  [ "small_data_0x0x4",   small_data,     0,  0,   0.5,  4   ],
  [ "multi_data_3x14x4",  multiple,       3, 14,   0.5,  4   ],
])

#-------------------------------------------------------------------------
# run_test
#-------------------------------------------------------------------------

def run_test( VvaddXcelType, test_params, cmdline_opts=None ):

  # Convert test data into byte array

  data = test_params.data
  data_src0 = data[::2]
  data_src1 = data[1::2]
  src0_bytes = [0]*len(data_src0)
  src1_bytes = [0]*len(data_src1)
  for i in range( len(data_src0) ):
    src0_bytes[i] = struct.pack("<{}I".format(len(data_src0[i])),*data_src0[i])
    src1_bytes[i] = struct.pack("<{}I".format(len(data_src1[i])),*data_src1[i])

  # Protocol messages

  xcel_protocol_msgs = []
  for i in range( len(data_src0) ):
    xcel_protocol_msgs = xcel_protocol_msgs + gen_xcel_protocol_msgs( len(data_src0[i]), i)
  xreqs  = xcel_protocol_msgs[::2]
  xresps = xcel_protocol_msgs[1::2]

  # Create test harness with protocol messagse

  th = TestHarness( VvaddXcelType )

  th.set_param( "top.src.construct", msgs=xreqs,
    initial_delay=test_params.src+3, interval_delay=test_params.src )

  th.set_param( "top.sink.construct", msgs=xresps,
    initial_delay=test_params.sink+3, interval_delay=test_params.sink )

  th.set_param( "top.mem.construct",
    stall_prob=test_params.stall, extra_latency=test_params.lat )

  # Load the data into the test memory

  th.elaborate()

  for i in range( len(data_src0) ):
    th.mem.write_mem( 0x1000 + 0x3000*i, src0_bytes[i] )
    th.mem.write_mem( 0x2000 + 0x3000*i, src1_bytes[i] )

  # Run the test

  run_sim( th, cmdline_opts, duts=['xcel'] )

  # Retrieve data from test memory

  result_bytes = [0]*len(data_src0)
  for i in range( len(data_src0) ):
    result_bytes[i] = th.mem.read_mem( 0x3000+ 0x3000*i, len(src0_bytes[i]) )

  for i in range( len(result_bytes) ):

    # Convert result bytes into list of ints
    result = list(struct.unpack("<{}I".format(len(data_src0[i])),result_bytes[i]))

    # Compare result
    for j in range( len(result) ):
      assert result[j] == data_src0[i][j] + data_src1[i][j]

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params ):
  run_test( VvaddXcelFL(), test_params )

