#=========================================================================
# ProcMemXcelFL_mix_test.py
#=========================================================================

import pytest

from pymtl3 import *
from proc.test.harness import asm_test
from pmx_v2.test.harness import run_test

from proc.ProcFL import ProcFL
from pmx_v2.NullXcelWideFL import NullXcelWideFL

from proc.test import inst_mix_beq_jal
from proc.test import inst_mix_mul_mem
from proc.test import inst_mix

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
    cls.XcelType   = NullXcelWideFL

  #-----------------------------------------------------------------------
  # mix_jal_beq
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_mix_beq_jal.gen_beq_jal_test      ),
    asm_test( inst_mix_beq_jal.gen_beq_nop_jal_test  ),
    asm_test( inst_mix_beq_jal.gen_beq_jalr_test     ),
    asm_test( inst_mix_beq_jal.gen_beq_nop_jalr_test ),
    asm_test( inst_mix_beq_jal.gen_jalr_jal_test     ),
    asm_test( inst_mix_beq_jal.gen_jalr_nop_jal_test ),
    asm_test( inst_mix_beq_jal.gen_many_beq_jal_test ),
  ])
  def test_jal_beq( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_jal_beq_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_mix_beq_jal.gen_many_beq_jal_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # mix_mul_mem
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_mix_mul_mem.gen_basic_test     ),
    asm_test( inst_mix_mul_mem.gen_more_test      ),
  ])
  def test_mul_mem( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_mul_mem_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_mix_mul_mem.gen_more_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # mix
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_mix.gen_mix_test     ),
  ])
  def test_mix( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_mix_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_mix.gen_mix_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

