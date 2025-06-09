#=========================================================================
# GCD Unit FL Model
#=========================================================================

from math import gcd

from pymtl3 import *

from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
from pymtl3.stdlib.stream      import IStreamDeqAdapterFL, OStreamEnqAdapterFL

from tut4_pymtl.gcd.GcdUnitMsg import GcdUnitMsgs

#-------------------------------------------------------------------------
# GcdUnitFL
#-------------------------------------------------------------------------

class GcdUnitFL( Component ):

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

    # FL block

    @update_once
    def block():
      if s.istream_q.deq.rdy() and s.ostream_q.enq.rdy():
        msg = s.istream_q.deq()
        s.ostream_q.enq( gcd(msg.a, msg.b) )

  # Line tracing

  def line_trace( s ):
    return f"{s.istream}(){s.ostream}"

