#! /usr/bin/python
# -*- coding: utf-8 -*-

from loguru import logger
import unittest

from PyQt5.QtWidgets import QApplication, QFileDialog

# import openslide
import pyqtgraph.parametertree
from pyqtgraph.parametertree import Parameter, ParameterTree

from exsu import param_tools as ptools
from exsu import dili
import collections
import pytest
import sys
import numpy as np

pytest_plugins = "pytester"


app = QApplication(sys.argv)


class ParameterTest(unittest.TestCase):

    # skip_on_local = False
    # skip_on_local = True
    # @unittest.skipIf(os.environ.get("TRAVIS", skip_on_local), "Skip on Travis-CI")

    def test_export_to_dict(self):
        params = [
            {
                "name": "Example Integer Param",
                "type": "int",
                "value": 224,
                "suffix": "px",
                "siPrefix": False,
                "tip": "Value defines size of something",
            },
            {
                "name": "Example Float Param",
                "type": "float",
                "value": 0.00006,
                "suffix": "m",
                "siPrefix": True,
                "tip": "Value defines size of something",
            },
            {
                "name": "subparam",
                "type": "group",
                "children": [
                    {"name": "sub 1", "value": 1, "type": "int"},
                    {"name": "sub 2", "value": 2, "type": "float"},
                ],
            },
        ]

        parameters = Parameter.create(
            name="first level",
            type="group",
            value=None,
            tip="tip message",
            children=params,
            expanded=False,
        )
        # mainapp = scaffan.Scaffan()
        dct = ptools.params_and_values(parameters)
        self.assertEqual(type(dct), dict)

        assert "subparam;sub 1" in dct

    def test_find_in_struct(self):
        params = [
            {
                "name": "Example Integer Param",
                "type": "int",
                "value": 224,
                "suffix": "px",
                "siPrefix": False,
                "tip": "Value defines size of something",
            },
            {
                "name": "Example Float Param",
                "type": "float",
                "value": 0.00006,
                "suffix": "m",
                "siPrefix": True,
                "tip": "Value defines size of something",
            },
            {
                "name": "subparam",
                "type": "group",
                "children": [
                    {"name": "sub 1", "value": 1, "type": "int"},
                    {"name": "sub 2", "value": 2, "type": "float"},
                ],
            },
        ]

        parameters = Parameter.create(
            name="first level",
            type="group",
            value=None,
            tip="tip message",
            children=params,
            expanded=False,
        )
        pgstruct = parameters.saveState()
        dct = ptools.from_pyqtgraph_struct(pgstruct)
        found = dili.find_in_struct(dct, "Example Float Param")
        assert found is not None

    def test_pyqtgraph_import_ordered_dict_and_back_again(self):
        cfg = collections.OrderedDict(
            [["bool", True], ["int", 5], ["str", "strdrr"], ["vs", [1.0, 2.5, 7]],]
        )
        captions = {"int": "toto je int"}
        pg_struct = ptools.to_pyqtgraph_struct("pokus", cfg)

        p = pyqtgraph.parametertree.Parameter.create(
            name="main", type="group", children=[pg_struct]
        )
        assert type(p) == pyqtgraph.parametertree.parameterTypes.GroupParameter
        logger.debug(f"pg_struct={pg_struct}")
        self.assertDictEqual(
            pg_struct["children"][0],
            {
                "type": "bool",
                "name": "bool",
                "value": True,
                "reconstruction_type": "bool",
            },
        )
        name_new, cfg_new = ptools.from_pyqtgraph_struct(pg_struct)
        assert "bool" in cfg_new

    def test_pyqtgraph_import_dict_and_back_again(self):
        cfg = {
            "bool param": True,
            "int param": 5,
            "str param": "strdrr",
            "vs": [1.0, 2.5, 7],
            # "ndarr param": np.asarray([[1,2], [3,4]])
        }
        captions = {"int": "toto je int"}
        pg_struct = ptools.to_pyqtgraph_struct("pokus", cfg)
        logger.debug(f"pg_struct={pg_struct}")
        self.assertDictEqual(
            pg_struct["children"][0],
            {
                "type": "bool",
                "name": "bool param",
                "value": True,
                "reconstruction_type": "bool",
            },
        )
        p = pyqtgraph.parametertree.Parameter.create(
            name=pg_struct["name"],
            type=pg_struct["type"],
            children=pg_struct["children"],
        )
        assert type(p) == pyqtgraph.parametertree.parameterTypes.GroupParameter
        pg_struct2 = p.saveState()

        name_new, cfg_new = ptools.from_pyqtgraph_struct(pg_struct)
        name_new2, cfg_new2 = ptools.from_pyqtgraph_struct(pg_struct2)
        assert "bool param" in cfg_new
        assert "bool param" in cfg_new2

    # @pytest.mark.interactive
    def test_dict_to_pyqtgraph_with_options(self):
        cfg = collections.OrderedDict(
            {
                "bool": True,
                "int": 5,
                "expected_float": 2,
                "str": "strdrr",
                "vs": [1.0, 2.5, 7]
                # 'Area Sampling' : dictwidgetpyqtgraph.AreaSamplingParameter(name='Area Sampling')
            }
        )
        captions = {"int": "toto je int"}

        opts = {}
        opts = {
            "children": {
                "vs": {
                    "title": "voxelsize",
                    "children": {
                        "0": {"title": "z", "suffix": "m", "siPrefix": True},
                        "1": {"title": "x", "suffix": "m", "siPrefix": True},
                        "2": {"title": "y", "suffix": "m", "siPrefix": True},
                    },
                },
                "expected_float": {"type": "float", "title": "Exp. float"},
            }
        }

        params = ptools.to_pyqtgraph_struct("params", cfg, opts=opts)
        params["children"].append(ptools.AreaSamplingParameter(name="Area Sampling"))
        # logger.debug(params)

        # params[0]['title'] = "Pokusny title"
        # params[0]['my note'] = "poznamka"

        p = Parameter.create(**params)
        # p = Parameter.create(name='params', type='group', children=params)
        t = ParameterTree()
        logger.debug(p.getValues())
        lst = p.saveState()
        vals = p.getValues()

        name, dict_again = ptools.from_pyqtgraph_struct(lst)
        assert name == "params"
        assert "expected_float" in dict_again
        assert dict_again["expected_float"] == 2.0
        t.setParameters(p, showTop=False)
        t.show()
        val_before0 = p.param("Area Sampling", "areasize_px", "0").value()
        val_before1 = p.param("Area Sampling", "areasize_mm", "0").value()
        p.param("Area Sampling", "voxelsize_mm", "0").setValue(0.3)
        val_after0 = p.param("Area Sampling", "areasize_px", "0").value()
        val_after1 = p.param("Area Sampling", "areasize_mm", "0").value()
        # TODO probably callback is not working
        # assert val_before0 != val_after0
        # assert val_before1 != val_after1

        # app.exec_()
        # assert False

    def test_pyqtgraph_find_pth_of_parameter(self):
        cfg = {
            "bool": True,
            "int": 5,
            "str": "strdrr",
            "vs": [1.0, 2.5, 7],
            "data": {"complex": {"real": 1.0, "imag": 0.5}},
            "real": 1.1,
        }
        captions = {"int": "toto je int"}
        pg_struct = ptools.to_pyqtgraph_struct("pokus", cfg)
        logger.debug(pg_struct)
        self.assertDictEqual(
            pg_struct["children"][0],
            {
                "type": "bool",
                "name": "bool",
                "value": True,
                "reconstruction_type": "bool",
            },
        )
        p = pyqtgraph.parametertree.Parameter.create(
            name="main", type="group", children=[pg_struct]
        )
        assert type(p) == pyqtgraph.parametertree.parameterTypes.GroupParameter

        params0 = ptools.find_parameter_path_by_fragment(p, "vs")
        assert len(params0) == 1
        assert params0[0] == "pokus;vs"

        params1 = ptools.find_parameter_path_by_fragment(p, "real")
        assert len(params1) == 2
        assert "pokus;data;complex;real" in params1

        params2 = ptools.find_parameter_path_by_fragment(p, "pokus")
        assert len(params2) == 1
        assert params2[0] == "pokus"

        params3 = ptools.find_parameter_path_by_fragment(p, "ex")
        assert len(params3) == 0

        params4 = ptools.find_parameter_path_by_fragment(p, "data;complex")
        assert len(params4) == 1


@pytest.fixture
def cfg_dict():
    cfg = {
        "bool": True,
        "int": 5,
        "str": "strdrr",
        "vs": [1.0, 2.5, 7],
        "data": {"complex": {"real": 1.0, "imag": 0.5}},
        "real": 1.1,
    }
    return cfg


def test_set_and_get_param_by_path(cfg_dict):
    cfg = cfg_dict

    captions = {"int": "toto je int"}
    pg_struct = ptools.to_pyqtgraph_struct("pokus", cfg)
    p = pyqtgraph.parametertree.Parameter.create(
        name=pg_struct["name"], type=pg_struct["type"], children=pg_struct["children"],
    )
    pths = ptools.find_parameter_path_by_fragment(p, "real")
    logger.debug(f"p.name={p.name()}")
    logger.debug(f"pths={pths}")
    logger.debug(f"pyqtgraph version={pyqtgraph.__version__}")
    logger.debug(f"pg_struct={pg_struct}")
    ptools.set_parameter_by_path(p, pths[0], 10)

    assert ptools.get_parameter_by_path(p, pths[0]).value() == 10

    ptools.set_parameter_by_path(p, pths[0], "10", literal_eval=True)
    assert (
        ptools.get_parameter_by_path(p, pths[0]).value() == 10
    ), "value set by string: '10' "

    pths_and_vals = list(zip(pths, [20, 30]))
    ptools.set_parameters_by_path(p, pths_and_vals)

    assert p.param("real").value() in [20, 30]
    assert p.param("data", "complex", "real").value() in [20, 30]

    # assert ptools.get_parameter_by_path(p, ["data", "complex", "real"], parse_path=False) in [20, 30], \
    #     "should be possible to get the parameter value by list"

    assert ptools.get_parameter_by_path(
        p, "data;complex;real", parse_path=True
    ).value() in [20, 30], "should be possible to get the parameter value by list"
