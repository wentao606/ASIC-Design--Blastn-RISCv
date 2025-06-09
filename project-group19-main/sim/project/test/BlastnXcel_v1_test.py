#=========================================================================
# blastnxcel_test.py
#=========================================================================

import pytest

from project.test.BlastnXcelFL_v1_test import TestHarness, test_case_table, run_test, run_test_multiple
from project.BlastnXcel_v1 import BlastnXcel_v1

@pytest.mark.parametrize( **test_case_table )
def test_ugpe(  cmdline_opts, test_params ):
  run_test( BlastnXcel_v1(), cmdline_opts, test_params )

def test_multiple( cmdline_opts ):
  run_test_multiple( BlastnXcel_v1(), cmdline_opts )
