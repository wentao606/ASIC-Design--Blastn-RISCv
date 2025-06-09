#=========================================================================
# ProcMemXcelFL_rr_test.py
#=========================================================================

import pytest

from pymtl3 import *
from proc.test.harness import asm_test
from pmx_v2.test.harness import run_test

from proc.ProcFL import ProcFL
from pmx_v2.NullXcelWideFL import NullXcelWideFL

from proc.test import inst_add
from proc.test import inst_sub
from proc.test import inst_mul
from proc.test import inst_and
from proc.test import inst_or
from proc.test import inst_xor
from proc.test import inst_slt
from proc.test import inst_sltu
from proc.test import inst_sra
from proc.test import inst_srl
from proc.test import inst_sll

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
  # add
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_add.gen_basic_test     ),
    asm_test( inst_add.gen_dest_dep_test  ),
    asm_test( inst_add.gen_src0_dep_test  ),
    asm_test( inst_add.gen_src1_dep_test  ),
    asm_test( inst_add.gen_srcs_dep_test  ),
    asm_test( inst_add.gen_srcs_dest_test ),
    asm_test( inst_add.gen_value_test     ),
    asm_test( inst_add.gen_random_test    ),
  ])
  def test_add( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_add_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_add.gen_random_test, translatable=s.translatable,
              delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # sub
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sub.gen_basic_test     ),
    asm_test( inst_sub.gen_dest_dep_test  ),
    asm_test( inst_sub.gen_src0_dep_test  ),
    asm_test( inst_sub.gen_src1_dep_test  ),
    asm_test( inst_sub.gen_srcs_dep_test  ),
    asm_test( inst_sub.gen_srcs_dest_test ),
    asm_test( inst_sub.gen_value_test     ),
    asm_test( inst_sub.gen_random_test    ),
  ])
  def test_sub( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_sub_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_sub.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # mul
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_mul.gen_basic_test     ),
    asm_test( inst_mul.gen_dest_dep_test  ),
    asm_test( inst_mul.gen_src0_dep_test  ),
    asm_test( inst_mul.gen_src1_dep_test  ),
    asm_test( inst_mul.gen_srcs_dep_test  ),
    asm_test( inst_mul.gen_srcs_dest_test ),
    asm_test( inst_mul.gen_value_test     ),
    asm_test( inst_mul.gen_random_test    ),
  ])
  def test_mul( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_mul_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_mul.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # and
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_and.gen_basic_test     ),
    asm_test( inst_and.gen_dest_dep_test  ),
    asm_test( inst_and.gen_src0_dep_test  ),
    asm_test( inst_and.gen_src1_dep_test  ),
    asm_test( inst_and.gen_srcs_dep_test  ),
    asm_test( inst_and.gen_srcs_dest_test ),
    asm_test( inst_and.gen_value_test     ),
    asm_test( inst_and.gen_random_test    ),
  ])
  def test_and( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable, cmdline_opts=s.__class__.cmdline_opts )

  def test_and_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_and.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # or
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_or.gen_basic_test     ),
    asm_test( inst_or.gen_dest_dep_test  ),
    asm_test( inst_or.gen_src0_dep_test  ),
    asm_test( inst_or.gen_src1_dep_test  ),
    asm_test( inst_or.gen_srcs_dep_test  ),
    asm_test( inst_or.gen_srcs_dest_test ),
    asm_test( inst_or.gen_value_test     ),
    asm_test( inst_or.gen_random_test    ),
  ])
  def test_or( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_or_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_or.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # xor
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_xor.gen_basic_test     ),
    asm_test( inst_xor.gen_dest_dep_test  ),
    asm_test( inst_xor.gen_src0_dep_test  ),
    asm_test( inst_xor.gen_src1_dep_test  ),
    asm_test( inst_xor.gen_srcs_dep_test  ),
    asm_test( inst_xor.gen_srcs_dest_test ),
    asm_test( inst_xor.gen_value_test     ),
    asm_test( inst_xor.gen_random_test    ),
  ])
  def test_xor( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_xor_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_xor.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # slt
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_slt.gen_basic_test     ),
    asm_test( inst_slt.gen_dest_dep_test  ),
    asm_test( inst_slt.gen_src0_dep_test  ),
    asm_test( inst_slt.gen_src1_dep_test  ),
    asm_test( inst_slt.gen_srcs_dep_test  ),
    asm_test( inst_slt.gen_srcs_dest_test ),
    asm_test( inst_slt.gen_value_test     ),
    asm_test( inst_slt.gen_random_test    ),
  ])
  def test_slt( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_slt_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_slt.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # sltu
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sltu.gen_basic_test     ),
    asm_test( inst_sltu.gen_dest_dep_test  ),
    asm_test( inst_sltu.gen_src0_dep_test  ),
    asm_test( inst_sltu.gen_src1_dep_test  ),
    asm_test( inst_sltu.gen_srcs_dep_test  ),
    asm_test( inst_sltu.gen_srcs_dest_test ),
    asm_test( inst_sltu.gen_value_test     ),
    asm_test( inst_sltu.gen_random_test    ),
  ])
  def test_sltu( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_sltu_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_sltu.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # sra
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sra.gen_basic_test     ),
    asm_test( inst_sra.gen_dest_dep_test  ),
    asm_test( inst_sra.gen_src0_dep_test  ),
    asm_test( inst_sra.gen_src1_dep_test  ),
    asm_test( inst_sra.gen_srcs_dep_test  ),
    asm_test( inst_sra.gen_srcs_dest_test ),
    asm_test( inst_sra.gen_value_test     ),
    asm_test( inst_sra.gen_random_test    ),
  ])
  def test_sra( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_sra_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_sra.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # srl
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_srl.gen_basic_test     ),
    asm_test( inst_srl.gen_dest_dep_test  ),
    asm_test( inst_srl.gen_src0_dep_test  ),
    asm_test( inst_srl.gen_src1_dep_test  ),
    asm_test( inst_srl.gen_srcs_dep_test  ),
    asm_test( inst_srl.gen_srcs_dest_test ),
    asm_test( inst_srl.gen_value_test     ),
    asm_test( inst_srl.gen_random_test    ),
  ])
  def test_srl( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_srl_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_srl.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # sll
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sll.gen_basic_test     ),
    asm_test( inst_sll.gen_dest_dep_test  ),
    asm_test( inst_sll.gen_src0_dep_test  ),
    asm_test( inst_sll.gen_src1_dep_test  ),
    asm_test( inst_sll.gen_srcs_dep_test  ),
    asm_test( inst_sll.gen_srcs_dest_test ),
    asm_test( inst_sll.gen_value_test     ),
    asm_test( inst_sll.gen_random_test    ),
  ])
  def test_sll( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_sll_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_sll.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

