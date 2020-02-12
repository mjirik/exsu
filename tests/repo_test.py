#! /usr/bin/python
# -*- coding: utf-8 -*-

from loguru import logger
import unittest
import os
from pathlib import Path
# import shutil
import pandas as pd
# import openslide
import exsu.report


def test_repo():
    report = exsu.report.Report(repodir=Path(repodir=Path(__file__).parent.parent.resolve()))
    report.finish_actual_row()
    print(report.df)
    assert report.df["repo exsu id"] is not None
    assert False
