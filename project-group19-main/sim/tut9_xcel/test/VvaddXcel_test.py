#=========================================================================
# VvaddXcel_test
#=========================================================================

import pytest

from tut9_xcel.test.VvaddXcelFL_test import test_case_table, run_test
from tut9_xcel.VvaddXcel import VvaddXcel

@pytest.mark.parametrize( **test_case_table )
def test( test_params, cmdline_opts ):
  run_test( VvaddXcel(), test_params, cmdline_opts )

