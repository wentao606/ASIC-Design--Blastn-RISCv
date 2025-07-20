#=========================================================================
# SeqRead Functional-Level (FL) Model
#=========================================================================

from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
from pymtl3.stdlib.stream import IStreamDeqAdapterFL, OStreamEnqAdapterFL

Bits128 = mk_bits(128)
Bits32 = mk_bits(32)
Bits16 = mk_bits(16)
Bits8 = mk_bits(8)

# Unpack 32-bit packed DNA (2-bit base-4 encoding) to list of 16 values
def unpack_data(val):
    return [ (val >> (2*i)) & 0x3 for i in range(16) ]
  
def slice_seq(query, database, q_start, d_start):
  
    if (q_start > d_start):
        right_len_min = 16 - q_start
        left_len_min = d_start  
    else:
        right_len_min = 16 - d_start
        left_len_min = q_start  

    hit_pos = left_len_min
    seq_len = left_len_min + right_len_min

    q_start_out = q_start
    d_start_out = d_start

    query = Bits32(query)
    database = Bits32(database)

    if (q_start > d_start):
      slice_database = zext(database[0 : ( seq_len ) * 2 ], 32)
      slice_query = zext(query[ (q_start - hit_pos) *2 : 32], 32)
    else:
      slice_query =  zext(query[ 0 : (seq_len ) * 2 ], 32)
      slice_database = zext(database[ (d_start - hit_pos)*2 : 32], 32)

    query_out = slice_query
    database_out =slice_database

    return query_out, database_out, q_start_out, d_start_out, hit_pos, seq_len

class SeqReadFL_v2 ( Component ):

  def construct( s ):

    s.istream = IStreamIfc( Bits128 )
    s.ostream = OStreamIfc( Bits128 )

    s.istream_q = IStreamDeqAdapterFL( Bits128 )
    s.ostream_q = OStreamEnqAdapterFL( Bits128 )

    s.istream //= s.istream_q.istream
    s.ostream //= s.ostream_q.ostream

    @update_once
    def block():
      if s.istream_q.deq.rdy() & s.ostream_q.enq.rdy():
        msg = s.istream_q.deq()

        query    = msg[ 0  : 32 ]
        database = msg[ 32 : 64 ]
        q_start  = msg[ 64 : 96 ]
        d_start  = msg[ 96 : 128 ]

        query_out, database_out, q_start_out, d_start_out, hit_pos, seq_len = slice_seq(
          query, database, q_start, d_start
        )

        out_msg = concat(
            trunc(seq_len, 16),
            trunc(hit_pos, 16),
            trunc(d_start_out, 16),
            trunc(q_start_out, 16),
            trunc(database_out, 32),
            trunc(query_out, 32),
        )

        s.ostream_q.enq( zext(out_msg, 128 ) )

  def line_trace( s ):
    return f"{s.istream} () {s.ostream}"
