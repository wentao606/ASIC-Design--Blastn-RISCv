#=========================================================================
# ProcMemXcelFL_vvadd_test.py
#=========================================================================

import pytest

from pymtl3 import *
from proc.test.harness import asm_test
from pmx_v2.test.harness import run_test

from proc.ProcFL import ProcFL
from tut9_xcel.VvaddXcelFL import VvaddXcelFL

from proc.test import inst_csr

#-------------------------------------------------------------------------
# Basic Xcel Test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """

    # initial array addresses and size

    csrr x1, mngr2proc < 0x00002000 # src0
    csrr x2, mngr2proc < 0x00002010 # src1
    csrr x3, mngr2proc < 0x00002020 # dest
    addi x4, x0, 4

    # use accelerator

    csrw 0x7e1, x1
    csrw 0x7e2, x2
    csrw 0x7e3, x3
    csrw 0x7e4, x4
    csrw 0x7e0, x0
    csrr x0,    0x7e0

    # verify results

    lw   x5, 0(x3)
    csrw proc2mngr, x5 > 6
    addi x3, x3, 4
    lw   x5, 0(x3)
    csrw proc2mngr, x5 > 8
    addi x3, x3, 4
    lw   x5, 0(x3)
    csrw proc2mngr, x5 > 10
    addi x3, x3, 4
    lw   x5, 0(x3)
    csrw proc2mngr, x5 > 12

    # data section

    .data

    # src0 (addr = 0x2000)
    .word 1
    .word 2
    .word 3
    .word 4

    # src1 (addr = 0x2010)
    .word 5
    .word 6
    .word 7
    .word 8

    # dest (addr = 0x2020)
    .word 0
    .word 0
    .word 0
    .word 0
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
    cls.XcelType   = VvaddXcelFL

  #-------------------------------------------------------------------------
  # csr
  #-------------------------------------------------------------------------

  def test_vvadd_nodelays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              gen_basic_test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_vvadd_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              gen_basic_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

