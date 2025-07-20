#=========================================================================
# ProcMemXcelFL_csr_test.py
#=========================================================================

import pytest

from pymtl3 import *
from proc.test.harness import asm_test
from pmx_v2.test.harness import run_test

from proc.ProcFL import ProcFL
from pmx_v2.NullXcelWideFL import NullXcelWideFL

from proc.test import inst_csr

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

  #-------------------------------------------------------------------------
  # csr
  #-------------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_csr.gen_basic_test      ),
    asm_test( inst_csr.gen_bypass_test     ),
    asm_test( inst_csr.gen_value_test      ),
    asm_test( inst_csr.gen_random_test     ),
    asm_test( inst_csr.gen_core_stats_test ),
  ])
  def test_csr( s, name, test ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

  def test_csr_delays( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              inst_csr.gen_random_test, translatable=s.translatable,
              delays=True, cmdline_opts=s.__class__.cmdline_opts )

