#=========================================================================
# ProcMemXcelFL_branch_test.py
#=========================================================================

import pytest

from pymtl3 import *
from proc.test.harness import asm_test
from pmx_v2.test.harness import run_test

from proc.ProcFL import ProcFL
from pmx_v2.NullXcelWideFL import NullXcelWideFL

from proc.test import inst_beq
from proc.test import inst_bne
from proc.test import inst_bge
from proc.test import inst_bgeu
from proc.test import inst_blt
from proc.test import inst_bltu

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
  # beq
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_beq.gen_basic_test ) ,
    asm_test( inst_beq.gen_src0_dep_taken_test    ),
    asm_test( inst_beq.gen_src0_dep_nottaken_test ),
    asm_test( inst_beq.gen_src1_dep_taken_test    ),
    asm_test( inst_beq.gen_src1_dep_nottaken_test ),
    asm_test( inst_beq.gen_srcs_dep_taken_test    ),
    asm_test( inst_beq.gen_srcs_dep_nottaken_test ),
    asm_test( inst_beq.gen_src0_eq_src1_test      ),
    asm_test( inst_beq.gen_value_test             ),
    asm_test( inst_beq.gen_random_test            ),
    asm_test( inst_beq.gen_back_to_back_test      ),
  ])
  def test_beq( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_beq_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_beq.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # bne
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_bne.gen_basic_test             ),
    asm_test( inst_bne.gen_src0_dep_taken_test    ),
    asm_test( inst_bne.gen_src0_dep_nottaken_test ),
    asm_test( inst_bne.gen_src1_dep_taken_test    ),
    asm_test( inst_bne.gen_src1_dep_nottaken_test ),
    asm_test( inst_bne.gen_srcs_dep_taken_test    ),
    asm_test( inst_bne.gen_srcs_dep_nottaken_test ),
    asm_test( inst_bne.gen_src0_eq_src1_test      ),
    asm_test( inst_bne.gen_value_test             ),
    asm_test( inst_bne.gen_random_test            ),
    asm_test( inst_bne.gen_back_to_back_test      ),
  ])
  def test_bne( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_bne_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_bne.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # bge
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_bge.gen_basic_test             ),
    asm_test( inst_bge.gen_src0_dep_taken_test    ),
    asm_test( inst_bge.gen_src0_dep_nottaken_test ),
    asm_test( inst_bge.gen_src1_dep_taken_test    ),
    asm_test( inst_bge.gen_src1_dep_nottaken_test ),
    asm_test( inst_bge.gen_srcs_dep_taken_test    ),
    asm_test( inst_bge.gen_srcs_dep_nottaken_test ),
    asm_test( inst_bge.gen_src0_eq_src1_test      ),
    asm_test( inst_bge.gen_value_test             ),
    asm_test( inst_bge.gen_random_test            ),
    asm_test( inst_bge.gen_back_to_back_test      ),
  ])
  def test_bge( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_bge_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_bge.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # bgeu
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_bgeu.gen_basic_test             ),
    asm_test( inst_bgeu.gen_src0_dep_taken_test    ),
    asm_test( inst_bgeu.gen_src0_dep_nottaken_test ),
    asm_test( inst_bgeu.gen_src1_dep_taken_test    ),
    asm_test( inst_bgeu.gen_src1_dep_nottaken_test ),
    asm_test( inst_bgeu.gen_srcs_dep_taken_test    ),
    asm_test( inst_bgeu.gen_srcs_dep_nottaken_test ),
    asm_test( inst_bgeu.gen_src0_eq_src1_test      ),
    asm_test( inst_bgeu.gen_value_test             ),
    asm_test( inst_bgeu.gen_random_test            ),
    asm_test( inst_bgeu.gen_back_to_back_test      ),
  ])
  def test_bgeu( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_bgeu_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_bgeu.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # blt
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_blt.gen_basic_test             ),
    asm_test( inst_blt.gen_src0_dep_taken_test    ),
    asm_test( inst_blt.gen_src0_dep_nottaken_test ),
    asm_test( inst_blt.gen_src1_dep_taken_test    ),
    asm_test( inst_blt.gen_src1_dep_nottaken_test ),
    asm_test( inst_blt.gen_srcs_dep_taken_test    ),
    asm_test( inst_blt.gen_srcs_dep_nottaken_test ),
    asm_test( inst_blt.gen_src0_eq_src1_test      ),
    asm_test( inst_blt.gen_value_test             ),
    asm_test( inst_blt.gen_random_test            ),
    asm_test( inst_blt.gen_back_to_back_test      ),
  ])
  def test_blt( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_blt_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_blt.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # bltu
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_bltu.gen_basic_test             ),
    asm_test( inst_bltu.gen_src0_dep_taken_test    ),
    asm_test( inst_bltu.gen_src0_dep_nottaken_test ),
    asm_test( inst_bltu.gen_src1_dep_taken_test    ),
    asm_test( inst_bltu.gen_src1_dep_nottaken_test ),
    asm_test( inst_bltu.gen_srcs_dep_taken_test    ),
    asm_test( inst_bltu.gen_srcs_dep_nottaken_test ),
    asm_test( inst_bltu.gen_src0_eq_src1_test      ),
    asm_test( inst_bltu.gen_value_test             ),
    asm_test( inst_bltu.gen_random_test            ),
    asm_test( inst_bltu.gen_back_to_back_test      ),
  ])
  def test_bltu( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_bltu_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_bltu.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

