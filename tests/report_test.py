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


    def test_imsave_npz_and_skimage(self):
        outputdir = Path("./test_report/")
        commonsheet = Path("./test_report_common_spreadsheet.xlsx")
        if commonsheet.exists():
            os.remove(commonsheet)
        fn = "test_image.png"
        fn_npz = Path("test_image.npz")
        fn_skimage = Path("test_image_skimage.png")
        if Path(fn).exists():
            os.remove(fn)
        if fn_npz.exists():
            os.remove(fn_npz)
        if fn_skimage.exists():
            os.remove(fn_skimage)

        img = 50 + np.random.rand(100, 100) * 30
        img[20:60, 20:60] += 100
        img = img.astype(np.uint8)
        report = exsu.report.Report(
            outputdir=outputdir, additional_spreadsheet_fn=commonsheet, level=50)
        report.imsave(fn, img, level=60, level_skimage=60, level_npz=60, k=1)

        assert (outputdir / fn).exists()
        assert (outputdir / fn_npz).exists()
        assert (outputdir / fn_skimage).exists()


    def test_imsave_npz_and_skimage_color(self):
        outputdir = Path("./test_report/")
        commonsheet = Path("./test_report_common_spreadsheet.xlsx")
        if commonsheet.exists():
            os.remove(commonsheet)
        fn = "test_image_color.png"
        fn_npz = Path("test_image_color.npz")
        fn_skimage = Path("test_image_color_skimage.png")
        if Path(fn).exists():
            os.remove(fn)
        if fn_npz.exists():
            os.remove(fn_npz)
        if fn_skimage.exists():
            os.remove(fn_skimage)

        img = 50 + np.random.rand(100, 100, 3) * 30
        img[20:60, 20:60, 0] += 100
        img[40:80, 20:60, 1] += 100
        img[40:60, 40:80, 2] += 100
        img = img.astype(np.uint8)
        report = exsu.report.Report(
            outputdir=outputdir, additional_spreadsheet_fn=commonsheet, level=50)
        report.imsave(fn, img, level=60, level_skimage=60, level_npz=60, k=1)

        assert (outputdir / fn).exists()
        assert (outputdir / fn_npz).exists()
        assert (outputdir / fn_skimage).exists()

    def test_savefig(self):
        outputdir = Path("./test_report/")
        commonsheet = Path("./test_report_common_spreadsheet.xlsx")
        if commonsheet.exists():
            os.remove(commonsheet)
        fn_noext = "test_figure"
        fn = "test_figure.png"

        fn_as_figure = "test_figure.png"
        # fn_npz = Path("test_figure.npz")
        # fn_skimage = Path("test_figure.png")
        if Path(fn).exists():
            os.remove(fn)
        # if fn_npz.exists():
        #     os.remove(fn_npz)
        # if fn_skimage.exists():
        #     os.remove(fn_skimage)
        #
        img = 50 + np.random.rand(100, 100, 3) * 30
        img[20:60, 20:60, 0] += 100
        img[40:80, 20:60, 1] += 100
        img[40:60, 40:80, 2] += 100
        img = img.astype(np.uint8)
        from matplotlib import pyplot as plt
        report = exsu.report.Report(
            outputdir=outputdir, additional_spreadsheet_fn=commonsheet, level=50
            # show=False
        )
        report.set_save(True)
        report.set_save(True)
        fig = plt.figure()
        report.savefig_and_show(fn_noext, fig=fig)
        plt.close() # probably not necessary

        # report.imsave(fn, img, level=60, level_skimage=60, level_npz=60, k=1)

        assert (outputdir / fn).exists()

        # test another function saving as figure
        report.imsave_as_fig(fn_as_figure)
        assert (outputdir / fn_as_figure).exists()
        # assert (outputdir / fn_npz).exists()
        # assert (outputdir / fn_skimage).exists()
