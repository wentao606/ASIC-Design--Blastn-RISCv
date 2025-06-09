#=========================================================================
# blastnxcel_test.py
#=========================================================================

import pytest

from project.test.BlastnXcelFL_v2_test import TestHarness, test_case_table, run_test, run_test_multiple
from project.BlastnXcel_v2 import BlastnXcel_v2

@pytest.mark.parametrize( **test_case_table )
def test_ugpe(  cmdline_opts, test_params ):
  run_test( BlastnXcel_v2(), cmdline_opts, test_params )

# def test_multiple( cmdline_opts ):
#   run_test_multiple( BlastnXcel_v2(), cmdline_opts )
