#=========================================================================
# UGPE Functional-Level (FL) Model
#=========================================================================

from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
from pymtl3.stdlib.stream import IStreamDeqAdapterFL, OStreamEnqAdapterFL


Bits256 = mk_bits(256)
Bits160 = mk_bits(160)
Bits128 = mk_bits(128)
Bits32 = mk_bits(32)
Bits16 = mk_bits(16)
Bits8 = mk_bits(8)

# Unpack 32-bit packed DNA (2-bit base-4 encoding) to list of 16 values
def unpack_data(val):
  return [ (val >> (2*i)) & 0x3 for i in range(16) ]
  
def ungapped_extend(query, database, q_start, d_start, hit_pos, seq_len):

  threshold = 20
  score_max = 0
  current_score = 0

  q_l_max = hit_pos -1 + 1
  q_r_max = hit_pos - 1
  d_l_max = hit_pos -1 +1
  d_r_max = hit_pos - 1

  q_l = hit_pos -1 + 1  # shift in opposite direction first
  q_r = hit_pos - 1     # shift in opposite direction first; start pos is the first of r part 
  d_l = hit_pos -1 + 1 
  d_r = hit_pos - 1

  while True:
    extended_l = False
    extended_r = False

    if (q_r < seq_len - 1) and (d_r < seq_len - 1):
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
        print("enter ")
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

  if ((q_l_max == hit_pos) and (q_r_max == hit_pos - 1 )):
  # if(q_r_max == q_l_max):
    length = 0
    q_l_max = hit_pos
    d_l_max = hit_pos
  else:
    length = q_r_max - q_l_max + 1
    # length = (q_r_max - (q_start-1)) + (q_l_max - q_start)
    
  q_start = q_start - (hit_pos - q_l_max)
  d_start = d_start - (hit_pos - d_l_max)
  return score_max, length, q_start, d_start

class UGPEFL_v2 ( Component ):

  def construct( s ):

    s.istream = IStreamIfc( Bits256 )
    s.ostream = OStreamIfc( Bits160 )

    s.istream_q = IStreamDeqAdapterFL( Bits256 )
    s.ostream_q = OStreamEnqAdapterFL( Bits160 )

    s.istream //= s.istream_q.istream
    s.ostream //= s.ostream_q.ostream

    @update_once
    def block():
      if s.istream_q.deq.rdy() & s.ostream_q.enq.rdy():
        msg = s.istream_q.deq()

        query    = msg[ 0  : 32 ]
        database = msg[ 32 : 64 ]
        q_start  = msg[ 64 : 80 ]
        d_start  = msg[ 80 : 96 ]
        hit_pos  = msg[ 96 : 112]
        seq_len  = msg[112 : 128]
        addr     = msg[128:160]

        query = query.uint()
        database = database.uint()
        hit_pos = hit_pos.uint()
        seq_len = seq_len.uint()
        d_start = d_start.uint()
        q_start = q_start.uint()
        q_list = unpack_data(query)
        d_list = unpack_data(database)

        score_max,length,q_start_out,d_start_out = ungapped_extend(
          q_list, d_list, q_start, d_start, hit_pos, seq_len
        )

        out_msg = concat(
          Bits128(addr),
          Bits8(d_start_out),
          Bits8(q_start_out),
          Bits8(length),
          Bits8(score_max)
        )

        s.ostream_q.enq( zext(out_msg, 32 ) )

  def line_trace( s ):
    return f"{s.istream} () {s.ostream}"
