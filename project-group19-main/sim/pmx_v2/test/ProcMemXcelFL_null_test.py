#=========================================================================
# ProcMemXcelFL_null_test.py
#=========================================================================

import pytest

from pymtl3 import *
from proc.test.harness import asm_test
from pmx_v2.test.harness import run_test

from proc.ProcFL import ProcFL
from pmx_v2.NullXcelWideFL import NullXcelWideFL

#-------------------------------------------------------------------------
# Basic Xcel Test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 1
    csrw 0x7e0, x1
    csrr x2, 0x7e0
    csrw proc2mngr, x2 > 1
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
    cls.XcelType   = NullXcelWideFL

  #-------------------------------------------------------------------------
  # null
  #-------------------------------------------------------------------------

  def test_null( s ):
    run_test( s.ProcType, s.ICacheType, s.DCacheType, s.XcelType,
              gen_basic_test, translatable=s.translatable,
              cmdline_opts=s.__class__.cmdline_opts )

