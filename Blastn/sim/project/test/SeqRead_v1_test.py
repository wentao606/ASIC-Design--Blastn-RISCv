#=========================================================================
# UGPE_test.py
#=========================================================================

import pytest

from pymtl3.stdlib.test_utils import run_sim
from project.test.SeqReadFL_v1_test import TestHarness, test_case_table
from project.SeqRead_v1 import SeqRead_v1

@pytest.mark.parametrize( **test_case_table )
def test_seqread( test_params, cmdline_opts ):

  th = TestHarness( SeqRead_v1() )

  th.set_param("top.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay+3,
    interval_delay=test_params.src_delay )

  th.set_param("top.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay+3,
    interval_delay=test_params.sink_delay )

  run_sim( th, cmdline_opts, duts=['seqread'] )
