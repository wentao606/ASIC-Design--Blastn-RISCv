#=========================================================================
# GCD Unit CL Model
#=========================================================================

from pymtl3 import *

from pymtl3.stdlib import stream

from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
from pymtl3.stdlib.stream      import IStreamDeqAdapterFL, OStreamEnqAdapterFL

from tut4_pymtl.gcd.GcdUnitMsg import GcdUnitMsgs

#-------------------------------------------------------------------------
# gcd
#-------------------------------------------------------------------------
# Helper function that uses Euclid's algorithm to calculate the greatest
# common denomiator, but also to estimate the number of cycles a simple
# FSM-based GCD unit might take.

def gcd_cl( a, b ):
  ncycles = 0
  while True:
    ncycles += 1
    if a < b:
      a,b = b,a
    elif b != 0:
      a = a - b
    else:
      return (a,ncycles)

#-------------------------------------------------------------------------
# GcdUnitCL
#-------------------------------------------------------------------------

class GcdUnitCL( Component ):

  # Constructor

  def construct( s ):

    # Interface

    s.istream = IStreamIfc( GcdUnitMsgs.req  )
    s.ostream = OStreamIfc( GcdUnitMsgs.resp )

    # Queue Adapters

    s.istream_q = IStreamDeqAdapterFL( GcdUnitMsgs.req  )
    s.ostream_q = OStreamEnqAdapterFL( GcdUnitMsgs.resp )

    s.istream //= s.istream_q.istream
    s.ostream //= s.ostream_q.ostream

    # Member variables

    s.result  = None
    s.counter = 0

    # CL block

    @update_once
    def block():

      if s.result is not None:
        # Handle delay to model the gcd unit latency
        if s.counter > 0:
          s.counter -= 1
        elif s.ostream_q.enq.rdy():
          s.ostream_q.enq( s.result )
          s.result = None

      elif s.istream_q.deq.rdy():
        msg = s.istream_q.deq()
        s.result, s.counter = gcd_cl(msg.a, msg.b)

  # Line tracing

  def line_trace( s ):
    return f"{s.istream}({s.counter:^4}){s.ostream}"
