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
import numpy as np


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

    def test_imsave(self):
        outputdir = Path("./test_report/")
        commonsheet = Path("./test_report_common_spreadsheet.xlsx")
        if commonsheet.exists():
            os.remove(commonsheet)
        fn = "test_image.png"
        img = 50 + np.random.rand(100, 100) * 30
        img[20:60, 20:60] += 100
        img = img.astype(np.uint8)
        report = exsu.report.Report(outputdir=outputdir, additional_spreadsheet_fn=commonsheet)
        report.imsave(fn, img)

        assert (outputdir / fn).exists()



