#=========================================================================
# ProcVvaddXcel_vvadd_test.py
#=========================================================================

from proc.Proc import Proc
from cache.Cache4B import Cache4B
from cache.Cache import Cache
from tut9_xcel.VvaddXcel import VvaddXcel

from pmx_v2.test.ProcMemXcelFL_vvadd_test import Tests as ProcMemXcelFL_vvadd_TestsBaseClass

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

class Tests( ProcMemXcelFL_vvadd_TestsBaseClass ):

  @classmethod
  def setup_class( cls ):
    cls.translatable = True
    cls.ProcType   = Proc
    cls.ICacheType = Cache4B
    cls.DCacheType = Cache
    cls.XcelType   = VvaddXcel

