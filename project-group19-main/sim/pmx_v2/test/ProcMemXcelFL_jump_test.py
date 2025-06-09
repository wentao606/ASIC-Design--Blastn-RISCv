#=========================================================================
# ProcMemXcelFL_jump_test.py
#=========================================================================

import pytest

from pymtl3 import *
from proc.test.harness import asm_test
from pmx_v2.test.harness import run_test

from proc.ProcFL import ProcFL
from pmx_v2.NullXcelWideFL import NullXcelWideFL

from proc.test import inst_jal
from proc.test import inst_jalr

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
  # jal
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_jal.gen_basic_test        ) ,
    asm_test( inst_jal.gen_link_dep_test     ) ,
    asm_test( inst_jal.gen_jump_test         ) ,
    asm_test( inst_jal.gen_back_to_back_test ) ,
    asm_test( inst_jal.gen_value_test_0      ) ,
    asm_test( inst_jal.gen_value_test_1      ) ,
    asm_test( inst_jal.gen_value_test_2      ) ,
    asm_test( inst_jal.gen_value_test_3      ) ,
    asm_test( inst_jal.gen_jal_stall_test    ) ,
  ])

  def test_jal( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_jal_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_jal.gen_jump_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # jalr
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_jalr.gen_basic_test    ),
    asm_test( inst_jalr.gen_link_dep_test    ),
    asm_test( inst_jalr.gen_jump_test        ),
    asm_test( inst_jalr.gen_lsb_test         ),
    asm_test( inst_jalr.gen_value_test_0     ),
    asm_test( inst_jalr.gen_value_test_1     ),
    asm_test( inst_jalr.gen_value_test_2     ),
    asm_test( inst_jalr.gen_value_test_3     ),
  ])

  def test_jalr( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_jalr_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_jalr.gen_jump_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

