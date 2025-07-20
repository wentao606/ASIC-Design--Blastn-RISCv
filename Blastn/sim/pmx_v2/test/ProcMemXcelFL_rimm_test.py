#=========================================================================
# ProcMemXcelFL_rimm_test.py
#=========================================================================

import pytest

from pymtl3 import *
from proc.test.harness import asm_test
from pmx_v2.test.harness import run_test

from proc.ProcFL import ProcFL
from pmx_v2.NullXcelWideFL import NullXcelWideFL

from proc.test import inst_addi
from proc.test import inst_andi
from proc.test import inst_ori
from proc.test import inst_xori
from proc.test import inst_slti
from proc.test import inst_sltiu
from proc.test import inst_srai
from proc.test import inst_srli
from proc.test import inst_slli
from proc.test import inst_lui
from proc.test import inst_auipc

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
  # addi
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_addi.gen_basic_test     ) ,
    asm_test( inst_addi.gen_dest_dep_test  ) ,
    asm_test( inst_addi.gen_src_dep_test   ) ,
    asm_test( inst_addi.gen_srcs_dest_test ) ,
    asm_test( inst_addi.gen_value_test     ) ,
    asm_test( inst_addi.gen_random_test    ) ,
  ])
  def test_addi( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_addi_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_addi.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # andi
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_andi.gen_basic_test     ) ,
    asm_test( inst_andi.gen_dest_dep_test  ) ,
    asm_test( inst_andi.gen_src_dep_test   ) ,
    asm_test( inst_andi.gen_srcs_dest_test ) ,
    asm_test( inst_andi.gen_value_test     ) ,
    asm_test( inst_andi.gen_random_test    ) ,
  ])
  def test_andi( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_andi_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_andi.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # ori
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_ori.gen_basic_test     ) ,
    asm_test( inst_ori.gen_dest_dep_test  ) ,
    asm_test( inst_ori.gen_src_dep_test   ) ,
    asm_test( inst_ori.gen_srcs_dest_test ) ,
    asm_test( inst_ori.gen_value_test     ) ,
    asm_test( inst_ori.gen_random_test    ) ,
  ])
  def test_ori( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_ori_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_ori.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # xori
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_xori.gen_basic_test     ) ,
    asm_test( inst_xori.gen_dest_dep_test  ) ,
    asm_test( inst_xori.gen_src_dep_test   ) ,
    asm_test( inst_xori.gen_srcs_dest_test ) ,
    asm_test( inst_xori.gen_value_test     ) ,
    asm_test( inst_xori.gen_random_test    ) ,
  ])
  def test_xori( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_xori_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_xori.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # slti
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_slti.gen_basic_test     ) ,
    asm_test( inst_slti.gen_dest_dep_test  ) ,
    asm_test( inst_slti.gen_src_dep_test   ) ,
    asm_test( inst_slti.gen_srcs_dest_test ) ,
    asm_test( inst_slti.gen_value_test     ) ,
    asm_test( inst_slti.gen_random_test    ) ,
  ])
  def test_slti( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_slti_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_slti.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # sltiu
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sltiu.gen_basic_test     ) ,
    asm_test( inst_sltiu.gen_dest_dep_test  ) ,
    asm_test( inst_sltiu.gen_src_dep_test   ) ,
    asm_test( inst_sltiu.gen_srcs_dest_test ) ,
    asm_test( inst_sltiu.gen_value_test     ) ,
    asm_test( inst_sltiu.gen_random_test    ) ,
  ])
  def test_sltiu( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_sltiu_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_sltiu.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # srai
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_srai.gen_basic_test     ) ,
    asm_test( inst_srai.gen_dest_dep_test  ) ,
    asm_test( inst_srai.gen_src_dep_test   ) ,
    asm_test( inst_srai.gen_srcs_dest_test ) ,
    asm_test( inst_srai.gen_value_test     ) ,
    asm_test( inst_srai.gen_random_test    ) ,
  ])
  def test_srai( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_srai_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_srai.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # srli
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_srli.gen_basic_test     ) ,
    asm_test( inst_srli.gen_dest_dep_test  ) ,
    asm_test( inst_srli.gen_src_dep_test   ) ,
    asm_test( inst_srli.gen_srcs_dest_test ) ,
    asm_test( inst_srli.gen_value_test     ) ,
    asm_test( inst_srli.gen_random_test    ) ,
  ])
  def test_srli( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_srli_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_srli.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # slli
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_slli.gen_basic_test     ) ,
    asm_test( inst_slli.gen_dest_dep_test  ) ,
    asm_test( inst_slli.gen_src_dep_test   ) ,
    asm_test( inst_slli.gen_srcs_dest_test ) ,
    asm_test( inst_slli.gen_value_test     ) ,
    asm_test( inst_slli.gen_random_test    ) ,
  ])
  def test_slli( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_slli_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_slli.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # lui
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_lui.gen_basic_test    ) ,
    asm_test( inst_lui.gen_dest_dep_test ) ,
    asm_test( inst_lui.gen_value_test    ) ,
    asm_test( inst_lui.gen_random_test   ) ,
  ])
  def test_lui( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_lui_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_lui.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # auipc
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_auipc.gen_basic_test    ) ,
    asm_test( inst_auipc.gen_dest_dep_test ) ,
    asm_test( inst_auipc.gen_value_test    ) ,
    asm_test( inst_auipc.gen_random_test   ) ,
  ])
  def test_auipc( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_auipc_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_auipc.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

