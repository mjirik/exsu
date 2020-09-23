# /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module provide simple interface to save experiment outputs directory with
spreadsheet and images.
"""
from loguru import logger
import pandas as pd
import os.path as op
import os
import warnings
from pathlib import Path
from typing import Union, List, Dict, Any
import numpy as np
from . import git_tools
from . import packages


class Report:
    def __init__(
        self,
        outputdir=None,
        additional_spreadsheet_fn=None,
        level=50,
        save=True,
        show=True,
        debug=False,
        repodir=None,
        reponame=None,
        check_version_of: List[str] = None,
    ):
        """
        :param repodir: Directory with repository. The repository is checked when it is added.
        Repository hash will be added to every row.
        :param reponame: Name of repository. It can be derived automatically from repodir.
        :param outputdir: Directory for output. Have to be set for image report.
        :param additional_spreadsheet_fn:
        :param level: control initial level
        :param save:
        :param show:
        :param debug:
        :param check_version_of: list of strings with names of packages. The versions of the packages are saved to
        output spreadsheet when the line is finished.
        """
        # self.outputdir = op.expanduser(outputdir)

        self.df: pd.DataFrame = None
        # self.imgs: Dict[str, np.ndarray] = {}
        self.imgs: dict = {}
        self.actual_row: dict = {}
        self.show = show
        self.save = save
        self.debug = debug
        self.level = level
        self.spreadsheet_fn = "data.xlsx"
        self.additional_spreadsheet_fn = additional_spreadsheet_fn
        self.persistent_cols: dict = {}
        # self.repos = []
        self.outputdir = None
        self.check_version_of = check_version_of

        if outputdir is not None:
            self.init_with_output_dir(outputdir)
        else:
            self.init()
        self.repos: dict = {}

        if repodir is not None:
            self.add_repo(repodir, reponame)

    def add_repo(self, repodir, reponame: str = None):
        # self.repos.push((repodir, reponame))
        self.repos[reponame] = Path(repodir)
        repo_cols = git_tools.repo_status_to_dict(repodir, reponame)
        self.set_persistent_cols(repo_cols)

    def set_persistent_cols(self, dct: dict, clear: bool = False):
        """
        Set data which will be appended to all rows.
        :param dct: dictionary with column name and value
        :param clear: True or False. Clear persistent cols before setting.
        :return:
        """
        if clear:
            self.persistent_cols = dct
        else:
            self.persistent_cols.update(dct)

        logger.debug(f"Adding persistent cols: {list(self.persistent_cols.keys())}")

    def init_with_output_dir(self, outputdir):
        """
        Make set_output_dir() and init report.
        :param outputdir:
        :return:
        """
        self.set_output_dir(outputdir)
        self.init()

    def set_output_dir(self, outputdir):
        """
        Set the output dir with expanrequired. .
        :param outputdir:
        :return:
        """
        self.outputdir = Path(outputdir).expanduser()
        # if not op.exists(self.outputdir):
        #     os.makedirs(self.outputdir)

    def set_show(self, show):
        self.show = show

    def set_save(self, save):
        self.save = save

    def add_cols_to_actual_row(self, data):
        self.actual_row.update(data)

    # def write_table(self, filename):
    def finish_actual_row(self):
        data = self.actual_row
        logger.trace(f"Actual row cols: {list(self.actual_row.keys())}")
        logger.trace(f"Persistent cols: {list(self.persistent_cols.keys())}")
        data.update(self.persistent_cols)
        if self.check_version_of is not None:
            data.update(packages.get_version_of_packages_as_dict(self.check_version_of))

        df = pd.DataFrame([list(data.values())], columns=list(data.keys()))
        logger.trace(
            f"Unique values types {np.unique(map(str, map(type, data.values())))}"
        )
        self.df = self.df.append(df, ignore_index=True)

        # if excel_path.exists():
        #     print("append to excel")
        #
        # else:
        #
        #     # writer = pd.ExcelWriter(filename, engine='openpyxl')
        #     df.to_excel(filename)
        #     print("create new excel")

        self.actual_row = {}

    # def add_table(self):
    #     pass

    def init(self):
        self.df = pd.DataFrame()
        self.imgs = {}
        self.actual_row = {}

    def dump(self):
        if self.outputdir is not None:
            pth = self.join_output_dir(self.spreadsheet_fn)
            logger.debug(f"Saving to file {pth}")
            ppth = Path(pth)
            if not ppth.parent.exists():
                logger.debug("creating output dir")
                os.makedirs(ppth.parent)
            self.df.to_excel(pth, index=False)

        if self.additional_spreadsheet_fn is not None:
            excel_path = Path(self.additional_spreadsheet_fn)
            # print("we will write to excel", excel_path)
            filename = str(excel_path)
            append_df_to_excel(filename, self.df)
        logger.debug(f"Saved")
        # append_df_to_excel_no_head_processing(filename, self.df)

    def imsave(
        self, base_fn, arr: np.ndarray, level=90, level_skimage=40, level_npz=20, k=50, kwargs_skimage=None, **kwargs
    ):
        """
        Save image to report dir.

        * The usual way is to use matplotlib to produce colored images from grayscale with no\
        additional stuff (like axes).

        * The alternative is to skimage to produce real grayscale. The\
        intensity values can easily overflow the uint8 range. It can be controled by the
        parameter 'k'.

        * The RAW data can be stored into .npz file format.

        :param base_fn: with a format slot for annotation id like "skeleton_{}.png"
        :param arr: numpy array with input data
        :param level: severity of input
        :param level_skimage: severity of input. It is not colloring the image.
        :param k: multiplier applied on input image intensities on skimage save
        :param kwargs_skimage: used for internal call of skimage.io.imsave
        :param kwargs are used for internal call plt.imsave
        :return:
        """

        import skimage.io
        if kwargs_skimage is None:
            kwargs_skimage = {}

        filename, ext = op.splitext(base_fn)
        if ext == "":
            ext = ".png"
        if self.save:
            if self._is_under_level(level):
                import matplotlib.pyplot as plt

                fn = self.join_output_dir(filename + ext)
                logger.debug(f"write to file: {fn}")
                plt.imsave(fn, arr, **kwargs)

            if self._is_under_level(level_skimage):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", ".*low contrast image.*")
                    ## warnings.simplefilter("low contrast image")
                    fn = self.join_output_dir(filename + "_skimage" + ext)
                    # if "check_contrast" not in kwargs_skimage:
                    #     kwargs_skimage["check_contrast"] = False
                    logger.debug(f"write to file: {fn}")
                    skimage.io.imsave(fn, k * arr, *kwargs_skimage)
            if self._is_under_level(level_npz):
                self._save_arr(base_fn, arr)

    def join_output_dir(self, *args, **kwargs):
        """
        Join path to output dir and create output dir if necessary
        :param args:
        :param kwargs:
        :return:
        """
        if self.outputdir is None:
            raise ValueError("Outputdir have to be set before file is saved.")
        if not op.exists(self.outputdir):
            os.makedirs(self.outputdir)
        return op.join(self.outputdir, *args, **kwargs)

    def _save_arr(self, base_fn, arr: np.ndarray):
        """
        Save ndarray to file and store file path to list
        :param base_fn:
        :param arr:
        :return:
        """
        filename, ext = op.splitext(base_fn)
        fn = self.join_output_dir(filename + ".npz")
        np.savez_compressed(fn, arr=arr)
        self.imgs[base_fn] = fn

    def load_array(self, base_fn) -> np.ndarray:
        """

        :param base_fn: read image source array from file based on base file name
        :return:
        """
        arr = np.load(self.imgs[base_fn])["arr"]
        # logger.debug(arr)

        return arr

    def imsave_as_fig(self, base_fn, arr, level=60, npz_level=30):
        """
        Save given array as figure and save array as npy as well.
        :param base_fn:
        :param arr:
        :param level:
        :return:
        """
        filename, ext = op.splitext(base_fn)
        if self._is_under_level(level):
            import matplotlib.pyplot as plt

            fig = plt.figure()
            plt.imshow(arr)
            plt.colorbar()
            if self.save:
                fn = self.join_output_dir(filename + "" + ext)
                plt.savefig(fn)
            if self.show:
                plt.show()
            else:
                plt.close(fig)
        if self._is_under_level(npz_level):
            self._save_arr(base_fn, arr)

    # def add_array(self, base_fn, arr, k=50):
    #     if self.save:
    #         self.imsave

    def savefig(self, base_fn, level=60):
        """
        Save figure with matploglib if severity is high enough.
        Do not close figure.

        :param base_fn: filename
        :param level: severity of input data
        :return:
        """
        import matplotlib.pyplot as plt

        if self._is_under_level(level):
            filename, ext = op.splitext(base_fn)
            if ext == "":
                ext = ".png"
            if self.save:
                fn = self.join_output_dir(filename + "" + ext)
                plt.savefig(fn)
                # self.imgs[base_fn] = [fn]

    def savefig_and_show(self, base_fn, fig, level=60):
        """
        Save figure with matploglib if severity is high enough and then show if
        report 'show' parameter is set true.

        :param base_fn: filename
        :param fig: figure id (used for closing figure if show is false)
        :param level: severity of input data
        :return:
        """
        import matplotlib.pyplot as plt

        self.savefig(base_fn, level=level)
        if self.show:
            plt.show()
        else:
            plt.close(fig)

    # def save_np_data(self, base_fn, data, format_args=None, level=60):
    #     if self._is_under_level(level):
    #         if format_args is None:
    #             format_args = []
    #         fn = self._imjoin(self.outputdir, base_fn.format(format_args))
    #         np.save(data, fn)
    #         self.imgs[base_fn] = fn

    def _is_under_level(self, level):
        return level_numeric_value(self.level) < level_numeric_value(level)


def level_numeric_value(level):
    """
    Convert string levels like 'debug' to number.
    :param level:
    :return:
    """
    if level is "debug":
        level = 10
    elif level is "info":
        level = 30
    elif level is "warning":
        level = 50
    return level


def append_df_to_excel(
    filename,
    df,
    sheet_name="Sheet1",
    startrow=None,
    truncate_sheet=False,
    **to_excel_kwargs,
):
    """
    Append a DataFrame [df] to existing Excel file [filename]
    into [sheet_name] Sheet.
    If [filename] doesn't exist, then this function will create it.

    Excel file have to be closed.

    Parameters:
      filename : File path or existing ExcelWriter
                 (Example: '/path/to/file.xlsx')
      df : dataframe to save to workbook
      sheet_name : Name of sheet which will contain DataFrame.
                   (default: 'Sheet1')
      startrow : upper left cell row to dump data frame.
                 Per default (startrow=None) calculate the last row
                 in the existing DF and write to the next row...
      truncate_sheet : truncate (remove and recreate) [sheet_name]
                       before writing DataFrame to Excel file
      to_excel_kwargs : arguments which will be passed to `DataFrame.to_excel()`
                        [can be dictionary]

    Returns: pandas dataframe with combined information
    """
    logger.debug(f"Writing XLSX to: {str(filename)}")
    # from openpyxl import load_workbook

    import pandas as pd

    filename = Path(filename)
    if filename.exists():
        # writer = pd.ExcelWriter(filename, engine='openpyxl')

        dfold = pd.read_excel(str(filename), sheet_name=sheet_name)
        # dfout = pd.concat([dfin, df], axis=0, ignore_index=True)
        dfcombine = dfold.append(df, ignore_index=True, sort=True)
        dfcombine.to_excel(str(filename), sheet_name=sheet_name, index=False)
        return dfcombine
        # try:
        #     dfold = pd.read_excel(str(filename), sheet_name=sheet_name)
        #     dfcombine = dfold.append(df, ignore_index=True)
        #     dfcombine.to_excel(str(filename), sheet_name=sheet_name)
        # except PermissionError as e:
        # print("File is opened in other application")
        # import xlwings as xw
        # sht = xw.Book(str(filename)).sheets[0]
        # sht.range('A1').expand().options(pd.DataFrame).value

    else:
        filename.parent.mkdir(parents=True, exist_ok=True)
        # pd.read_excel(filename, sheet_name=)
        df.to_excel(str(filename), sheet_name=sheet_name, index=False)
        return df

    # # ignore [engine] parameter if it was passed
    # if 'engine' in to_excel_kwargs:
    #     to_excel_kwargs.pop('engine')
    #
    # writer = pd.ExcelWriter(filename, engine='openpyxl')
    #
    # # Python 2.x: define [FileNotFoundError] exception if it doesn't exist
    # try:
    #     FileNotFoundError
    # except NameError:
    #     FileNotFoundError = IOError
    #
    #
    # try:
    #     # try to open an existing workbook
    #     writer.book = load_workbook(filename)
    #
    #     # get the last row in the existing Excel sheet
    #     # if it was not specified explicitly
    #     if startrow is None and sheet_name in writer.book.sheetnames:
    #         startrow = writer.book[sheet_name].max_row
    #
    #     # truncate sheet
    #     if truncate_sheet and sheet_name in writer.book.sheetnames:
    #         # index of [sheet_name] sheet
    #         idx = writer.book.sheetnames.index(sheet_name)
    #         # remove [sheet_name]
    #         writer.book.remove(writer.book.worksheets[idx])
    #         # create an empty sheet [sheet_name] using old index
    #         writer.book.create_sheet(sheet_name, idx)
    #
    #     # copy existing sheets
    #     writer.sheets = {ws.title:ws for ws in writer.book.worksheets}
    # except FileNotFoundError:
    #     # file does not exist yet, we will create it
    #     pass
    #
    # if startrow is None:
    #     startrow = 0
    #
    # # write out the new sheet
    # df.to_excel(writer, sheet_name, startrow=startrow, **to_excel_kwargs)
    #
    # # save the workbook
    # writer.save()


# def append_df_to_excel_no_head_processing(filename, df, sheet_name='Sheet1', startrow=None,
#                                           truncate_sheet=False,
#                                           **to_excel_kwargs):
#     """
#
#     Append a DataFrame [df] to existing Excel file [filename]
#     into [sheet_name] Sheet.
#     If [filename] doesn't exist, then this function will create it.
#     It does insert also first line with column name :-(
#
#     Parameters:
#       filename : File path or existing ExcelWriter
#                  (Example: '/path/to/file.xlsx')
#       df : dataframe to save to workbook
#       sheet_name : Name of sheet which will contain DataFrame.
#                    (default: 'Sheet1')
#       startrow : upper left cell row to dump data frame.
#                  Per default (startrow=None) calculate the last row
#                  in the existing DF and write to the next row...
#       truncate_sheet : truncate (remove and recreate) [sheet_name]
#                        before writing DataFrame to Excel file
#       to_excel_kwargs : arguments which will be passed to `DataFrame.to_excel()`
#                         [can be dictionary]
#
#     Returns: None
#     """
#     # from openpyxl import load_workbook
#
#     import pandas as pd
#
#     # ignore [engine] parameter if it was passed
#     if 'engine' in to_excel_kwargs:
#         to_excel_kwargs.pop('engine')
#
#     writer = pd.ExcelWriter(filename, engine='openpyxl')
#
#     # Python 2.x: define [FileNotFoundError] exception if it doesn't exist
#     try:
#         FileNotFoundError
#     except NameError:
#         FileNotFoundError = IOError
#
#
#     try:
#         # try to open an existing workbook
#         from openpyxl import load_workbook
#         writer.book = load_workbook(filename)
#
#         # get the last row in the existing Excel sheet
#         # if it was not specified explicitly
#         if startrow is None and sheet_name in writer.book.sheetnames:
#             startrow = writer.book[sheet_name].max_row
#
#         # truncate sheet
#         if truncate_sheet and sheet_name in writer.book.sheetnames:
#             # index of [sheet_name] sheet
#             idx = writer.book.sheetnames.index(sheet_name)
#             # remove [sheet_name]
#             writer.book.remove(writer.book.worksheets[idx])
#             # create an empty sheet [sheet_name] using old index
#             writer.book.create_sheet(sheet_name, idx)
#
#         # copy existing sheets
#         writer.sheets = {ws.title:ws for ws in writer.book.worksheets}
#     except FileNotFoundError:
#         # file does not exist yet, we will create it
#         pass
#
#     if startrow is None:
#         startrow = 0
#
#     # write out the new sheet
#     df.to_excel(writer, sheet_name, startrow=startrow, **to_excel_kwargs)
#
#     # save the workbook
#     writer.save()
