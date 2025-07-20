#=========================================================================
# ProcMemXcelFL_accum_test.py
#=========================================================================

import pytest

from pymtl3 import *
from proc.test.harness import asm_test
from pmx_v2.test.harness import run_test

from proc.ProcFL import ProcFL
from tut9_xcel.AccumXcelFL import AccumXcelFL

from proc.test import inst_csr

#-------------------------------------------------------------------------
# Basic Xcel Test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """

    # initial array addresses and size

    csrr x1, mngr2proc < 0x00002000 # src
    addi x2, x0, 4

    # use accelerator

    csrw 0x7e1, x1
    csrw 0x7e2, x2
    csrw 0x7e0, x0
    csrr x3,    0x7e0

    # verify results

    csrw proc2mngr, x3 > 10

    # data section

    .data

    # src0 (addr = 0x2000)
    .word 1
    .word 2
    .word 3
    .word 4
  """

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

@pytest.mark.usefixtures("cmdline_opts")
class Tests:

  @classmethod
  def setup_class( cls ):
    cls.translatable = False
    cls.ProcType   = ProcFL
    cls.ICacheType = None
    cls.DCacheType = None
    cls.XcelType   = AccumXcelFL

  #-------------------------------------------------------------------------
  # csr
  #-------------------------------------------------------------------------

  def test_accum_nodelays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              gen_basic_test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_accum_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              gen_basic_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

