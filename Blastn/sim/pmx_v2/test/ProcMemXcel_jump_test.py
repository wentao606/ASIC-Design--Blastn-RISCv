#=========================================================================
# ProcMemXcel_jump_test.py
#=========================================================================

from proc.Proc import Proc
from cache.Cache4B import Cache4B
from cache.Cache import Cache
from pmx_v2.NullXcelWide import NullXcelWide

from pmx_v2.test.ProcMemXcelFL_jump_test import Tests as ProcMemXcelFL_jump_TestsBaseClass

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

class Tests( ProcMemXcelFL_jump_TestsBaseClass ):

  @classmethod
  def setup_class( cls ):
    cls.translatable = True
    cls.ProcType   = Proc
    cls.ICacheType = Cache4B
    cls.DCacheType = Cache
    cls.XcelType   = NullXcelWide

