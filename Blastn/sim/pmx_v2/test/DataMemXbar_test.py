#=========================================================================
# DataMemXbar_test
#=========================================================================

import pytest

from random import seed, randint

from pymtl3 import *

from pymtl3.stdlib.mem        import MemoryFL, mk_mem_msg, MemMsgType
from pymtl3.stdlib.stream     import StreamSourceFL, StreamSinkFL
from pymtl3.stdlib.test_utils import run_sim, mk_test_case_table

from pmx_v2.DataMemXbar import DataMemXbar

#-------------------------------------------------------------------------
# Message Types
#-------------------------------------------------------------------------

MemReqMsg4B,  MemRespMsg4B  = mk_mem_msg( 8, 32, 32  )

def dreq( type_, opaque, addr, len, data ):
  if   type_ == 'rd': type_ = MemMsgType.READ
  elif type_ == 'wr': type_ = MemMsgType.WRITE
  elif type_ == 'in': type_ = MemMsgType.WRITE_INIT

  return MemReqMsg4B( type_, opaque, addr, len, data)

def dresp( type_, opaque, test, len, data ):
  if   type_ == 'rd': type_ = MemMsgType.READ
  elif type_ == 'wr': type_ = MemMsgType.WRITE
  elif type_ == 'in': type_ = MemMsgType.WRITE_INIT

  return MemRespMsg4B( type_, opaque, test, len, data )

MemReqMsg16B, MemRespMsg16B = mk_mem_msg( 8, 32, 128 )

def xreq( type_, opaque, addr, len, data ):
  if   type_ == 'rd': type_ = MemMsgType.READ
  elif type_ == 'wr': type_ = MemMsgType.WRITE
  elif type_ == 'in': type_ = MemMsgType.WRITE_INIT

  return MemReqMsg16B( type_, opaque, addr, len, data)

def xresp( type_, opaque, test, len, data ):
  if   type_ == 'rd': type_ = MemMsgType.READ
  elif type_ == 'wr': type_ = MemMsgType.WRITE
  elif type_ == 'in': type_ = MemMsgType.WRITE_INIT

  return MemRespMsg16B( type_, opaque, test, len, data )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s ):

    # Instantiate models

    s.dsrc  = StreamSourceFL( MemReqMsg4B )
    s.dsink = StreamSinkFL( MemRespMsg4B )

    s.xsrc  = StreamSourceFL( MemReqMsg16B )
    s.xsink = StreamSinkFL( MemRespMsg16B )

    s.xbar  = DataMemXbar()
    s.mem   = MemoryFL( 1, [(MemReqMsg16B,MemRespMsg16B)] )

    # Connect

    s.dsrc.ostream    //= s.xbar.dmem.reqstream
    s.dsink.istream   //= s.xbar.dmem.respstream

    s.xsrc.ostream    //= s.xbar.xmem.reqstream
    s.xsink.istream   //= s.xbar.xmem.respstream

    s.xbar.mem        //= s.mem.ifc[0]

  def done( s ):
    return s.dsrc.done() and s.dsink.done() and \
           s.xsrc.done() and s.xsink.done()

  def line_trace( s ):
    return s.dsrc.line_trace() + "|" + s.xsrc.line_trace() + " > " \
         + s.mem.line_trace() + " > " \
         + s.dsink.line_trace() + "|" + s.xsink.line_trace()

#-------------------------------------------------------------------------
# basic_dmsgs
#-------------------------------------------------------------------------

def basic_dmsgs():
  return [
    #     type  opq  addr   len data                 type  opq  test len data
    dreq( 'wr', 0x0, 0x1000, 0, 0x04030201 ), dresp( 'wr', 0x0, 0,   0,  0          ),
    dreq( 'wr', 0x0, 0x1004, 0, 0x08070605 ), dresp( 'wr', 0x0, 0,   0,  0          ),
    dreq( 'wr', 0x0, 0x1008, 0, 0x0c0b0a09 ), dresp( 'wr', 0x0, 0,   0,  0          ),
    dreq( 'wr', 0x0, 0x100c, 0, 0x0f0e0d0c ), dresp( 'wr', 0x0, 0,   0,  0          ),

    dreq( 'rd', 0x0, 0x1000, 0, 0          ), dresp( 'rd', 0x0, 0,   0,  0x04030201 ),
    dreq( 'rd', 0x0, 0x1004, 0, 0          ), dresp( 'rd', 0x0, 0,   0,  0x08070605 ),
    dreq( 'rd', 0x0, 0x1008, 0, 0          ), dresp( 'rd', 0x0, 0,   0,  0x0c0b0a09 ),
    dreq( 'rd', 0x0, 0x100c, 0, 0          ), dresp( 'rd', 0x0, 0,   0,  0x0f0e0d0c ),
  ]

#-------------------------------------------------------------------------
# basic_xmsgs
#-------------------------------------------------------------------------

def basic_xmsgs():
  return [
    #     type  opq  addr   len data                                            type  opq  test len data
    xreq( 'wr', 0x0, 0x2000, 4, 0xabcdef02_cafeefac_c0ffee00_deadbeef ), xresp( 'wr', 0x0, 0,   4,  0          ),
    xreq( 'wr', 0x0, 0x2004, 4, 0xdeadbeef_abcdef02_cafeefac_c0ffee00 ), xresp( 'wr', 0x0, 0,   4,  0          ),
    xreq( 'wr', 0x0, 0x2008, 4, 0xc0ffee02_deadbeef_abcdef02_cafeefac ), xresp( 'wr', 0x0, 0,   4,  0          ),
    xreq( 'wr', 0x0, 0x200c, 4, 0xcafeefac_c0ffee02_deadbeef_abcdef02 ), xresp( 'wr', 0x0, 0,   4,  0          ),

    xreq( 'rd', 0x0, 0x2000, 4, 0                                     ), xresp( 'rd', 0x0, 0,   4,  0xdeadbeef ),
    xreq( 'rd', 0x0, 0x2004, 4, 0                                     ), xresp( 'rd', 0x0, 0,   4,  0xc0ffee00 ),
    xreq( 'rd', 0x0, 0x2008, 4, 0                                     ), xresp( 'rd', 0x0, 0,   4,  0xcafeefac ),
    xreq( 'rd', 0x0, 0x200c, 4, 0                                     ), xresp( 'rd', 0x0, 0,   4,  0xabcdef02 ),
  ]

#-------------------------------------------------------------------------
# random_dmsgs
#-------------------------------------------------------------------------

def random_dmsgs():

  seed(0xdeadbeef)

  vmem = 16*[0]
  msgs = []

  # First write 16 addresses

  for i in range(0,16):
    vmem[i] = i
    msgs.extend([
      dreq( 'wr', 0, 0x00001000+4*i, 0, i ), dresp( 'wr', 0, 0, 0, 0 ),
    ])

  # Now lots of random accesses

  for i in range(100):
    idx = randint(0,15)

    if randint(0,1):

      correct_data = vmem[idx]
      msgs.extend([
        dreq( 'rd', 0, 0x00001000+4*idx, 0, 0 ), dresp( 'rd', 0, 0, 0, correct_data ),
      ])

    else:

      new_data = randint(0,0xffffffff)
      vmem[idx] = new_data
      msgs.extend([
        dreq( 'wr', i, 0x00001000+4*idx, 0, new_data ), dresp( 'wr', 0, 0, 0, 0 ),
      ])

  # Read all data again to make sure every write was correct

  for i in range(0,16):
    correct_data = vmem[i]
    msgs.extend([
      dreq( 'rd', i, 0x00001000+4*i, 0, 0 ), dresp( 'rd', 0, 0, 0, correct_data ),
    ])

  return msgs

#-------------------------------------------------------------------------
# random_xmsgs
#-------------------------------------------------------------------------

def random_xmsgs():

  seed(0xc0ffee00)

  vmem = 16*[0]
  msgs = []

  # First write 16 addresses

  for i in range(0,16):
    vmem[i] = i
    msgs.extend([
      xreq( 'wr', 0, 0x00002000+4*i, 4, i ), xresp( 'wr', 0, 0, 4, 0 ),
    ])

  # Now lots of random accesses

  for i in range(100):
    idx = randint(0,15)

    if randint(0,1):

      correct_data = vmem[idx]
      msgs.extend([
        xreq( 'rd', 0, 0x00002000+4*idx, 4, 0 ), xresp( 'rd', 0, 0, 4, correct_data ),
      ])

    else:

      new_data = randint(0,0xffffffff)
      vmem[idx] = new_data
      msgs.extend([
        xreq( 'wr', i, 0x00002000+4*idx, 4, new_data ), xresp( 'wr', 0, 0, 4, 0 ),
      ])

  # Read all data again to make sure every write was correct

  for i in range(0,16):
    correct_data = vmem[i]
    msgs.extend([
      xreq( 'rd', i, 0x00002000+4*i, 4, 0 ), xresp( 'rd', 0, 0, 4, correct_data ),
    ])

  return msgs

#-------------------------------------------------------------------------
# run_test
#-------------------------------------------------------------------------

def run_test( test_params, cmdline_opts=None ):

  # Instantiate test harness

  th = TestHarness()

  # Generate messages

  dmsgs = test_params.dmsg_func()
  xmsgs = test_params.xmsg_func()

  # Set parameters

  th.set_param("top.dsrc.construct",
    msgs=dmsgs[::2],
    initial_delay=test_params.src+3,
    interval_delay=test_params.src )

  th.set_param("top.dsink.construct",
    msgs=dmsgs[1::2],
    initial_delay=test_params.sink+3,
    interval_delay=test_params.sink )

  th.set_param("top.xsrc.construct",
    msgs=xmsgs[::2],
    initial_delay=test_params.src+3,
    interval_delay=test_params.src )

  th.set_param("top.xsink.construct",
    msgs=xmsgs[1::2],
    initial_delay=test_params.sink+3,
    interval_delay=test_params.sink )

  th.set_param( "top.mem.construct",
    stall_prob=test_params.stall,
    extra_latency=test_params.lat )

  th.elaborate()

  # Run the test

  run_sim( th, cmdline_opts, duts=['xbar'] )

#-------------------------------------------------------------------------
# test
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                      "dmsg_func     xmsg_func     stall lat src sink"),
  [ "basic",              basic_dmsgs,  basic_xmsgs,  0.0,  0,  0,  0    ],
  [ "random",             random_dmsgs, random_xmsgs, 0.0,  0,  0,  0    ],
  [ "random_sink_delay1", random_dmsgs, random_xmsgs, 0.2,  0,  0,  1    ],
  [ "random_src_delay1",  random_dmsgs, random_xmsgs, 0.2,  0,  1,  0    ],
  [ "random_both_delay1", random_dmsgs, random_xmsgs, 0.2,  0,  1,  1    ],
  [ "random_sink_delay3", random_dmsgs, random_xmsgs, 0.5,  3,  0,  3    ],
  [ "random_src_delay3",  random_dmsgs, random_xmsgs, 0.5,  3,  3,  0    ],
  [ "random_both_delay3", random_dmsgs, random_xmsgs, 0.5,  3,  3,  3    ],
  [ "random_sink_delay8", random_dmsgs, random_xmsgs, 0.5,  3,  0,  8    ],
  [ "random_src_delay8",  random_dmsgs, random_xmsgs, 0.5,  3,  8,  0    ],
  [ "random_both_delay8", random_dmsgs, random_xmsgs, 0.5,  3,  8,  8    ],
])

@pytest.mark.parametrize( **test_case_table )
def test( test_params, cmdline_opts ):
  run_test( test_params, cmdline_opts )
