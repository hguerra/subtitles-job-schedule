# -*- coding: utf-8 -*-

import pytest
from subtitles_job_schedule.skeleton import fib

__author__ = "Heitor Carneiro"
__copyright__ = "Heitor Carneiro"
__license__ = "mit"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
