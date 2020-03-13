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
import exsu.git_tools


def test_repo():
    """
    Test non repo dir
    :return:
    """
    pth1 = Path(__file__).parent.parent.resolve().absolute()
    pth2 = Path(__file__).parent.parent.parent.resolve().absolute()
    logger.debug(f"pth1:{pth1}")
    logger.debug(f"pth2:{pth2}")
    rows_git_repo = exsu.git_tools.repo_status_to_dict(repodir=pth1)
    rows_not_git_repo = exsu.git_tools.repo_status_to_dict(repodir=pth2)
    assert len(rows_git_repo) > len(rows_not_git_repo)


def test_repo_in_report():
    report = exsu.report.Report(repodir=Path(__file__).parent.parent.resolve())
    report.finish_actual_row()
    print(report.df)
    assert report.df["repo exsu id"] is not None
