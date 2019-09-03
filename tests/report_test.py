#! /usr/bin/python
# -*- coding: utf-8 -*-

from loguru import logger
import unittest
import os
import io3d
from pathlib import Path
import shutil
import pandas as pd


# import openslide
import exsu.report



class ReportTest(unittest.TestCase):

    skip_on_local = False
    # skip_on_local = True
    # @unittest.skipIf(os.environ.get("TRAVIS", skip_on_local), "Skip on Travis-CI")
    def test_save_report_excel(self):
        outputdir = Path("./test_report/")
        # if outputdir.exists():
        #     shutil.rmtree(outputdir)
        commonsheet = Path("./test_report_common_spreadsheet.xlsx")
        if commonsheet.exists():
            os.remove(commonsheet)

        report = exsu.report.Report(outputdir=outputdir, additional_spreadsheet_fn=commonsheet)
        report.add_cols_to_actual_row({"Col1": 25, "Col2": "test string", "Col5": 5})
        report.add_cols_to_actual_row({"Col2": "prepsanu", "Col1": 26, "Col4": "ctyrka"})
        report.finish_actual_row()

        report.add_cols_to_actual_row({"Col1": 27, "Col2": "test string", "Col3": "trojka"})
        report.finish_actual_row()
        report.dump()

        # new write to common excel
        report.init()
        report.add_cols_to_actual_row({"Col1": 28, "Col2": "new line to common", "Col7": 77})
        report.finish_actual_row()
        report.dump()

        df = pd.read_excel(commonsheet)
        self.assertEqual(len(df), 3, "3 lines expected in the excel file")


