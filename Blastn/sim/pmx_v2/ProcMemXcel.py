#=========================================================================
# ProcMemXcel
#=========================================================================
# Full system which can either include the processor, xcel, icache,
# dcache, and dmemxbar, or optionally can just include the processor and
# xcel.

from pymtl3 import *
from pymtl3.passes.backends.verilog import *

from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
from pymtl3.stdlib.mem.ifcs    import MemRequesterIfc
from pymtl3.stdlib.mem         import mk_mem_msg

from pmx_v2.DataMemXbar import DataMemXbar

class ProcMemXcel( Component ):

  def construct( s, ProcType, ICacheType, DCacheType, XcelType ):

    s.cache_en = ICacheType != None and DCacheType != None

    MemReqMsg4B,  MemRespMsg4B  = mk_mem_msg( 8, 32, 32 )
    MemReqMsg16B, MemRespMsg16B = mk_mem_msg( 8, 32, 128 )

    # Proc/Mngr Interface

    s.stats_en    = OutPort()
    s.commit_inst = OutPort()

    s.mngr2proc = IStreamIfc( Bits32 )
    s.proc2mngr = OStreamIfc( Bits32 )

    # If caches are included then the interface is just the icache and
    # dcache main memory interfaces, otherwise the interface is three
    # memory interfaces for imem, dmem, and xmem

    if s.cache_en:
      s.imem = MemRequesterIfc( MemReqMsg16B, MemRespMsg16B )
      s.dmem = MemRequesterIfc( MemReqMsg16B, MemRespMsg16B )
    else:
      s.imem = MemRequesterIfc( MemReqMsg4B,  MemRespMsg4B  )
      s.dmem = MemRequesterIfc( MemReqMsg4B,  MemRespMsg4B  )
      s.xmem = MemRequesterIfc( MemReqMsg16B, MemRespMsg16B )

    # Instantiate processor and xcel

    s.proc = ProcType()
    s.xcel = XcelType()

    # Optionally include caches and data xbar

    if s.cache_en:
      s.icache = ICacheType()
      s.dcache = DCacheType()
      s.dxbar  = DataMemXbar()

    # Connect processor to xcel

    s.xcel.xcel //= s.proc.xcel

    # Connections if caches are included

    if s.cache_en:
      s.icache.proc2cache //= s.proc.imem

      s.dxbar.dmem //= s.proc.dmem
      s.dxbar.xmem //= s.xcel.mem
      s.dcache.proc2cache //= s.dxbar.mem

      s.imem //= s.icache.cache2mem
      s.dmem //= s.dcache.cache2mem

    # Connections if caches are not included

    else:
      s.imem //= s.proc.imem
      s.dmem //= s.proc.dmem
      s.xmem //= s.xcel.mem

    # Pass proc/mngr interface up to top-level

    s.mngr2proc //= s.proc.mngr2proc
    s.proc2mngr //= s.proc.proc2mngr

    # Processor core id is hard coded to zero

    s.proc.core_id //= 0

    # Pass other signals up to top-level

    s.stats_en    //= s.proc.stats_en
    s.commit_inst //= s.proc.commit_inst

    # Explicit module name

    if s.cache_en:
      s.set_metadata( VerilogTranslationPass.explicit_module_name,
                      f"ProcMemXcel_{XcelType.__name__}" )
    else:
      s.set_metadata( VerilogTranslationPass.explicit_module_name,
                      f"ProcXcel_{XcelType.__name__}" )

  def line_trace( s ):
    if s.cache_en:
      return s.proc.line_trace() + "[" + s.icache.line_trace() \
             + "|" + s.dxbar.line_trace() + s.dcache.line_trace() + "]" \
             + s.xcel.line_trace()
    else:
      return s.proc.line_trace() + s.xcel.line_trace()

