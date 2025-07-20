#=========================================================================
# harness
#=========================================================================

import struct
import pytest

from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
from pymtl3.stdlib.stream import StreamSourceFL, StreamSinkFL
from pymtl3.stdlib.mem import MemoryFL, mk_mem_msg, MemMsgType
from pymtl3.stdlib.test_utils import run_sim

from proc.tinyrv2_encoding import assemble

from pmx_v2.ProcMemXcel import ProcMemXcel

#=========================================================================
# TestHarness
#=========================================================================

class TestHarness( Component ):

  #-----------------------------------------------------------------------
  # constructor
  #-----------------------------------------------------------------------

  def construct( s, ProcType, ICacheType, DCacheType, XcelType ):

    s.cache_en = ICacheType != None and DCacheType != None

    # Interface

    s.stats_en    = OutPort()
    s.commit_inst = OutPort()

    # Instantiate source and system

    s.src  = StreamSourceFL( Bits32, [] )
    s.sink = StreamSinkFL( Bits32, [] )
    s.sys  = ProcMemXcel( ProcType, ICacheType, DCacheType, XcelType )

    # System <-> Proc/Mngr

    s.src.ostream //= s.sys.mngr2proc
    s.sys.proc2mngr //= s.sink.istream

    # Instantiate memory - if cache is enabled we need two
    # 128b ports for the icache and dcache main memory interface; if
    # cache is not enabled we need three ports for directly
    # connecting imem, dmem, and xmem interfaces

    if s.cache_en:
      s.mem = MemoryFL(2, mem_ifc_dtypes=2*[mk_mem_msg(8,32,128)] )
      s.sys.imem //= s.mem.ifc[0]
      s.sys.dmem //= s.mem.ifc[1]

    else:
      s.mem = MemoryFL(3, mem_ifc_dtypes=[mk_mem_msg(8,32,32),
                                          mk_mem_msg(8,32,32),mk_mem_msg(8,32,128)] )
      s.sys.imem //= s.mem.ifc[0]
      s.sys.dmem //= s.mem.ifc[1]
      s.sys.xmem //= s.mem.ifc[2]

    # Bring the stats enable up to the top level

    s.stats_en    //= s.sys.stats_en
    s.commit_inst //= s.sys.commit_inst

  #-----------------------------------------------------------------------
  # load memory image
  #-----------------------------------------------------------------------

  def load( self, mem_image ):

    # Iterate over the sections

    sections = mem_image.get_sections()
    for section in sections:

      # For .mngr2proc sections, copy section into mngr2proc src

      if section.name == ".mngr2proc":
        for bits in struct.iter_unpack("<I", section.data):
          self.src.msgs.append( b32(bits[0]) )

      # For .proc2mngr sections, copy section into proc2mngr_ref src

      elif section.name == ".proc2mngr":
        for bits in struct.iter_unpack("<I", section.data):
          self.sink.msgs.append( b32(bits[0]) )

      # For all other sections, simply copy them into the memory

      else:
        start_addr = section.addr
        stop_addr  = section.addr + len(section.data)
        self.mem.mem.mem[start_addr:stop_addr] = section.data

  #-----------------------------------------------------------------------
  # cleanup
  #-----------------------------------------------------------------------

  def cleanup( s ):
    del s.mem.mem[:]

  #-----------------------------------------------------------------------
  # done
  #-----------------------------------------------------------------------

  def done( s ):
    return s.src.done() and s.sink.done()

  #-----------------------------------------------------------------------
  # line trace
  #-----------------------------------------------------------------------

  def line_trace( s ):

    imem_reqstr = "  "
    if s.mem.ifc[0].reqstream.val and s.mem.ifc[0].reqstream.rdy:
      imem_reqstr = MemMsgType.str[int(s.mem.ifc[0].reqstream.msg.type_)]

    imem_respstr = "  "
    if s.mem.ifc[0].respstream.val and s.mem.ifc[0].respstream.rdy:
      imem_respstr = MemMsgType.str[int(s.mem.ifc[0].respstream.msg.type_)]

    imem_str = "     "
    if imem_reqstr != "  " or imem_respstr != "  ":
      imem_str = f"{imem_reqstr}>{imem_respstr}"

    dmem_reqstr = "  "
    if s.mem.ifc[1].reqstream.val and s.mem.ifc[1].reqstream.rdy:
      dmem_reqstr = MemMsgType.str[int(s.mem.ifc[1].reqstream.msg.type_)]

    dmem_respstr = "  "
    if s.mem.ifc[1].respstream.val and s.mem.ifc[1].respstream.rdy:
      dmem_respstr = MemMsgType.str[int(s.mem.ifc[1].respstream.msg.type_)]

    dmem_str = "     "
    if dmem_reqstr != "  " or dmem_respstr != "  ":
      dmem_str = f"{dmem_reqstr}>{dmem_respstr}"

    mem_str = f"{imem_str}|{dmem_str}"

    if not s.cache_en:

      xmem_reqstr = "  "
      if s.mem.ifc[2].reqstream.val and s.mem.ifc[2].reqstream.rdy:
        xmem_reqstr = MemMsgType.str[int(s.mem.ifc[2].reqstream.msg.type_)]

      xmem_respstr = "  "
      if s.mem.ifc[2].respstream.val and s.mem.ifc[2].respstream.rdy:
        xmem_respstr = MemMsgType.str[int(s.mem.ifc[2].respstream.msg.type_)]

      xmem_str = "     "
      if xmem_reqstr != "  " or xmem_respstr != "  ":
        xmem_str = f"{xmem_reqstr}>{xmem_respstr}"

      mem_str += f"|{xmem_str}"

    return ("*" if s.sys.stats_en else " ") + \
           s.src.line_trace() + " >" + \
           s.sys.line_trace() + " " + \
           mem_str + " > " + \
           s.sink.line_trace()

#=========================================================================
# run_test
#=========================================================================

def run_test( ProcType, ICacheType, DCacheType, XcelType,
              gen_test, translatable=False,
              delays=False, cmdline_opts=None ):

  # If the model is not translatable but the user has specified
  # --test-verilog then skip this test

  if not translatable and cmdline_opts != None:
    if cmdline_opts['test_verilog'] != '':
       pytest.skip("skipping untranslatable test cases with --test-verilog")

  # Instantiate model

  model = TestHarness( ProcType, ICacheType, DCacheType, XcelType )

  # Set parameters

  if delays:

    model.set_param( "top.src.construct",
                     initial_delay=0, interval_delay=20,
                     interval_delay_mode='random' )

    model.set_param( "top.sink.construct",
                     initial_delay=0, interval_delay=20,
                     interval_delay_mode='random' )

    model.set_param( "top.mem.construct",
                     stall_prob=0.5, extra_latency=3 )

  model.elaborate()

  asm_prog = None
  if isinstance( gen_test, str ):
    asm_prog = gen_test
  else:
    asm_prog = gen_test()

  # print(asm_prog)
  mem_image = assemble( asm_prog )
  model.load( mem_image )

  run_sim( model, cmdline_opts, duts=['sys'] )

