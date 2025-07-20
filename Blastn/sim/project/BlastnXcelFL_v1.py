#=========================================================================
# blastn_v1 Unit FL Model
#=========================================================================


from pymtl3 import *
from pymtl3.stdlib.mem.ifcs  import MemRequesterIfc
from pymtl3.stdlib.mem       import MemMsgType, mk_mem_msg
from pymtl3.stdlib.mem       import MemRequesterAdapterFL
from pymtl3.stdlib.xcel.ifcs import XcelResponderIfc
from pymtl3.stdlib.xcel      import XcelMsgType, mk_xcel_msg
from pymtl3.stdlib.stream    import OStreamBlockingAdapterFL
from pymtl3.stdlib.stream    import IStreamBlockingAdapterFL

def blastn_xcel(query, database, q_start, d_start ):

  threshold = 20
  score_max = 0
  current_score = 0

  q_l_max = q_start
  q_r_max = q_start
  d_l_max = d_start
  d_r_max = d_start

  q_l = q_start -1 + 1  # shift in opposite direction first
  q_r = q_start -1      # shift in opposite direction first; start pos is the first of r part 
  d_l = d_start -1 + 1 
  d_r = d_start -1 


  while True:
    extended_l = False
    extended_r = False


    if (q_r < len(query) - 1) and (d_r < len(database) - 1):
      q_r += 1
      d_r += 1
      if query[q_r] == database[d_r]:
        current_score += 1
      else:
        current_score -= 3
      extended_r = True

    if (q_l > 0 ) and (d_l > 0 ):
      q_l -= 1
      d_l -= 1
      if query[q_l] == database[d_l]:
        current_score += 1
      else:
        current_score -= 3
      extended_l = True

    if (not extended_l) and (not extended_r):
      break

    if current_score >= score_max:
      score_max = current_score

      # aligned length is the same so record max pos of either q or d is fine
      q_l_max = q_l 
      q_r_max = q_r 
      d_l_max = d_l
      d_r_max = d_r

    if (score_max - current_score) > threshold:
      break

  
  if (q_r_max - q_l_max != d_r_max - d_l_max):
    print("ERROR")

  if(q_r_max == q_l_max):
    length = 0
  else:
    length = q_r_max - q_l_max + 1
    # length = (q_r_max - (q_start-1)) + (q_l_max - q_start)
    
  q_start = q_l_max
  d_start = d_l_max
  return score_max, length, q_start, d_start
  


class BlastnXcelFL_v1( Component ):

  def construct( s ):
    MemReqMsg,  MemRespMsg  = mk_mem_msg( 8, 32, 32 )
    XcelReqMsg, XcelRespMsg = mk_xcel_msg( 5, 32 )

    # Interface

    s.xcel = XcelResponderIfc( XcelReqMsg, XcelRespMsg )
    s.mem  = MemRequesterIfc( MemReqMsg, MemRespMsg )

    # Proc <-> Xcel Adapters

    s.xcelreq_q  = IStreamBlockingAdapterFL( XcelReqMsg  )
    s.xcelresp_q = OStreamBlockingAdapterFL( XcelRespMsg )

    connect( s.xcelreq_q.istream,  s.xcel.reqstream  )
    connect( s.xcelresp_q.ostream, s.xcel.respstream )

    # Xcel <-> Memory Adapters

    s.mem_adapter = MemRequesterAdapterFL( MemReqMsg, MemRespMsg )

    connect( s.mem, s.mem_adapter.requester )
 

    # value
    s.q_start = 0
    s.d_start = 0
    s.query = 0
    s.database = 0 


    @update_once
    def up_blastn_xcel():

      # We loop handling accelerator requests. We are only expecting
      # writes to xr0-2, so any other requests are an error. We exit the
      # loop when we see the write to xr0.

      go = False
      while not go:

        xcelreq_msg = s.xcelreq_q.deq()

        if xcelreq_msg.type_ == XcelMsgType.WRITE:
          assert xcelreq_msg.addr in [0,1,2,3,4], \
            "Only reg writes to 0,1,2,3,4 allowed during setup!"

          # Use xcel register address to configure accelerator

          if xcelreq_msg.addr == 0: go = True
          if xcelreq_msg.addr   == 1: s.query    = xcelreq_msg.data
          elif xcelreq_msg.addr == 2: s.database = xcelreq_msg.data
          elif xcelreq_msg.addr == 3: s.q_start  = xcelreq_msg.data
          elif xcelreq_msg.addr == 4: s.d_start  = xcelreq_msg.data
          # Send xcel response message
          s.xcelresp_q.enq( XcelRespMsg( XcelMsgType.WRITE, 0 ) )
      
      # xcelreq_msg = s.xcelreq_q.deq()

      # s.xcelresp_q.enq( XcelRespMsg( XcelMsgType.READ, 1 ) )

      query = []
      database = []

      for i in range(16):
        query.append( (s.query >> (2*i)) & 0x3 )
        database.append( (s.database >> (2*i)) & 0x3 )

      score_out, length_out, q_start_out, d_start_out = \
        blastn_xcel(query, database, s.q_start, s.d_start )


      write_back = False

      while not write_back:
        xcelreq_msg = s.xcelreq_q.deq()

        if xcelreq_msg.type_ == XcelMsgType.READ:
          assert xcelreq_msg.addr in [0,1,2,3,4], \
            "Only reg reads to 0,1,2,3,4 allowed during sduring result phase!"

          # Use xcel register address to configure accelerator

          if xcelreq_msg.addr == 0: 
            write_back = True  
            s.xcelresp_q.enq( XcelRespMsg( XcelMsgType.READ, 1 ) )
          if xcelreq_msg.addr   == 1: s.xcelresp_q.enq( XcelRespMsg( XcelMsgType.READ, score_out ) )
          elif xcelreq_msg.addr == 2: s.xcelresp_q.enq( XcelRespMsg( XcelMsgType.READ, length_out ) )
          elif xcelreq_msg.addr == 3: s.xcelresp_q.enq( XcelRespMsg( XcelMsgType.READ, q_start_out ) )
          elif xcelreq_msg.addr == 4: s.xcelresp_q.enq( XcelRespMsg( XcelMsgType.READ, d_start_out ) )

      # xcelreq_msg = s.xcelreq_q.deq()

      # s.xcelresp_q.enq( XcelRespMsg( XcelMsgType.READ, 1 ) )


  # Line tracing

  def line_trace( s ):
    return f"{s.xcel.reqstream}(){s.xcel.respstream}"

