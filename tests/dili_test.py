#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from loguru import logger
import numpy as np

import unittest
from collections import OrderedDict
from exsu import dili
import pytest


def test_get_fcn_params():
    def test_fcn(a, b, c=1, d=2):
        return a + b + c

    class MyTestObj:
        def __init__(self, oa, ob, oc=1, od=2):
            pass

    myobj = MyTestObj(1, 2)
    argsf = dili.get_default_kwargs(test_fcn)
    argso = dili.get_default_kwargs(MyTestObj)
    argsi = dili.get_default_kwargs(myobj)
    logger.debug(f"argsf: {argsf}")
    assert argsf["c"] == 1
    assert argso["oc"] == 1
    assert argsi["oc"] == 1


class DictListTestCase(unittest.TestCase):
    def generate_dict_data(self):
        data = {"a": 1, "b": 2, "c": {"aa": 11, "bb": 22, "cc": {"aaa": 111}}}
        return data

    def test_ditc_flatten(self):
        data = {"a": 1, "b": 2, "c": {"aa": 11, "bb": 22, "cc": {"aaa": 111}}}
        dct = dili.flatten_dict(data)
        dct = dict(dct)
        self.assertIn("cccaaa", dct.keys())

    def test_ditc_flatten_keys_with_simplify(self):
        data = {"a": 1, "b": 2, "c": {"aa": 11, "bb": 22, "cc": {"aaa": [1,2,0]}}}
        dct = dili.flatten_dict_join_keys(data, simplify_iterables=True)
        dct = dict(dct)
        assert "c cc aaa 0" in dct.keys()
        assert dct["c cc aaa 0"] == 1

    def test_dict_flatten_with_separator(self):
        data = {"a": 1, "b": 2, "c": {"aa": 11, "bb": 22, "cc": {"aaa": 111}}}
        dct = dili.flatten_dict(data, separator=";")
        dct = dict(dct)
        self.assertIn("c;cc;aaa", dct.keys())

    def test_dict_recursive_update(self):
        data = self.generate_dict_data()
        data_updated = dili.recursive_update(data, {"c": {"aa": 33}})
        self.assertEqual(data_updated["c"]["aa"], 33)

    def test_list_to_dict(self):
        data = self.generate_dict_data()
        data["c"]["here is list"] = [1, 2, 5]

        data_with_dict = dili.list_to_dict_in_structure(data)
        dct = data_with_dict["c"]["here is list"]
        self.assertEqual(type(dct), dict)
        assert data_with_dict["c"]["here is list"][2] == 5

    def test_list_to_dict_key_str(self):
        data = self.generate_dict_data()
        data["c"]["here is list"] = [1, 2, 5]

        data_with_dict = dili.list_to_dict_in_structure(data, keys_to_str=True)
        dct = data_with_dict["c"]["here is list"]
        self.assertEqual(type(dct), dict)
        assert data_with_dict["c"]["here is list"]['2'] == 5

    def test_ndarray_to_list(self):
        data = self.generate_dict_data()
        data["c"]["here is ndarray"] = np.asarray([1, 2, 5])

        data_with_list = dili.ndarray_to_list_in_structure(data)
        self.assertEqual(type(data_with_list["c"]["here is ndarray"]), list)

    def test_dict_split(self):
        data = self.generate_dict_data()
        ab, c = dili.split_dict(data, ["a", "b"])
        self.assertIn("a", ab.keys())
        self.assertIn("b", ab.keys())
        self.assertIn("c", c.keys())

    def test_dict_subdict(self):
        data = self.generate_dict_data()

        ab = dili.subdict(data, ["a", "b"])
        self.assertIn("a", ab.keys())
        self.assertIn("b", ab.keys())
        # self.assertIn("c", c.keys())

    def test_split_dict_ordered(self):
        data = OrderedDict([("pear", 1), ("orange", 2), ("banana", 3), ("apple", 4)])
        ab, c = dili.split_dict(data, ["pear", "banana"])
        self.assertIn("pear", ab.keys())
        self.assertIn("banana", ab.keys())
        self.assertIn("apple", c.keys())

    def test_kick_from_dict(self):
        data = self.generate_dict_data()
        dct = dili.kick_from_dict(data, ["a", "b"])
        self.assertNotIn("a", dct.keys())
        self.assertNotIn("b", dct.keys())
        self.assertIn("c", dct.keys())

    def test_find_subsring_in_list(self):
        lst = ["auto", "veloco", "toto", "cola"]
        output = dili.list_contains(lst, "co")

        self.assertIn("veloco", output)
        self.assertIn("cola", output)

    def test_list_filter(self):
        lst = ["aa", "sss", "aaron", "rew"]
        output = dili.list_filter(lst, notstartswith="aa")
        self.assertTrue(["sss", "rew"] == output)

    def test_dict_find_key(self):
        slab = {"liver": 1, "porta": 2}
        val = dili.dict_find_key(slab, 2)
        self.assertEqual(val, "porta")

    # def test_dict_find_key_error(self):
    #     slab={"liver": 1, "porta": 2}
    #     val = dili.dict_find_key(slab, 3)
    #     self.assertEqual(val, "porta")
    def sort_list_data(self):
        dct = [
            {"name": "mira", "age": 34, "height": 172.0, "weight": 75},
            {"name": "kamca", "age": 25, "height": 152.0, "weight": 55},
            {"name": "bob", "age": 34, "height": 183.0, "weight": 85},
            {"name": "pavel", "age": 34, "height": 179.0, "weight": 98},
            {"name": "veru", "age": 25, "height": 162.0, "weight": 60},
            {"name": "pepa", "age": 39, "height": 182.0, "weight": 130},
        ]
        return dct

    def test_sort_list_of_dicts(self):
        dct = self.sort_list_data()

        dct = dili.sort_list_of_dicts(dct, keys=["age", "height"])
        self.assertEqual(dct[0]["name"], "kamca")
        self.assertEqual(dct[1]["name"], "veru")
        self.assertEqual(dct[2]["name"], "mira")
        self.assertEqual(dct[-1]["name"], "pepa")

    def test_sort_list_of_dicts_single_key(self):
        dct = self.sort_list_data()
        dct = dili.sort_list_of_dicts(dct, keys="height")
        self.assertEqual(dct[0]["name"], "kamca")
        # self.assertEqual(dct[1]["name"], "veru")
        # self.assertEqual(dct[2]["name"], "mira")
        self.assertEqual(dct[-1]["name"], "bob")

    def test_ordered_dict_to_dict(self):
        from collections import OrderedDict

        od = OrderedDict()
        od["klkj"] = 1
        od["here is dict"] = {"s": 1, 1: 17}
        od["list"] = ["uuu", 146, ["sdf", 18]]
        od2 = OrderedDict()
        od2["as"] = 1
        od2["as2"] = 1
        od["ordered dict"] = od2

        normal_dict = dili.ordered_dict_to_dict(od)
        self.assertEqual(type(normal_dict), dict)

    def test_drop_duplicates(self):
        import pandas as pd

        df = pd.DataFrame(
            {
                "col1": [5, 5, 1],
                "col2": [2, 2, 3],
                "time1": [1, 7, 9],
                "time2": [9, 7, 5],
            }
        )
        dfn = dili.df_drop_duplicates(df, "time")
        # self.assertEqual(len(dfn.keys()), 2)
        self.assertEqual(len(dfn), 2)

    def test_find_in_list_of_lists(self):
        lst = [[5, 6, 7], [1, 13], [2, 9]]
        self.assertEqual(dili.find_in_list_of_lists(lst, 7), 0)
        self.assertEqual(dili.find_in_list_of_lists(lst, 13), 1)
        self.assertEqual(dili.find_in_list_of_lists(lst, 9), 2)
        self.assertEqual(dili.find_in_list_of_lists(lst, 50), None)

    def test_find_value_in_struct(self):

        struct = {
            "bool": True,
            "int": 5,
            "str": "strdrr",
            "vs": [1.0, 2.5, 7],
            "data": {"complex": {"real": 1.0, "imag": 0.5}},
            "real": 1.1,
        }

        dfn = dili.find_value_in_struct(struct, 5)
        assert len(dfn) > 0
        # self.assertEqual(len(dfn.keys()), 2)
        # self.assertEqual(len(dfn), 2)

    def test_find_in_struct(self):
        struct = {
            "bool": True,
            "int": 5,
            "str": "strdrr",
            "vs": [1.0, 2.5, 7],
            "data": {"complex": {"real": 1.0, "imag": 0.5}},
            "real": 1.1,
        }

        dfn = dili.find_in_struct(struct, "bool")
        assert dfn == ["bool"]

        dfn = dili.find_in_struct(struct, ["complex", "data"])
        # this is probably not expected behavior
        assert dfn == ["data", "complex", "real"]

        dfn = dili.find_in_struct(struct, "real")
        assert dfn == ["data", "complex", "real"]

        val = dili.pick_from_struct(struct, dfn)
        val = 100

        dili.set_in_struct(struct, dfn, 10)
        assert struct["data"]["complex"]["real"] == 10


def test_find_closest_in_pandas():
    import pandas as pd
    df1 = pd.DataFrame({
            "x": [0.0, 0.0, 1.0, 1.0],
            "y": [0.0, 1.0, 1.0, 1.5],
    })
    df2 = pd.DataFrame({
        "x": [0.1, 1.1, 0.1, 1.1],
        "y": [0.1, 1.0, 1.0, 1.5],
    })

    ids = dili.find_id_of_nearest(df1, key=["x", "y"], df2=df2, key2=["x", "y"])
    assert all(list(ids) == np.asarray([0, 2, 1, 3]))

    ids = dili.find_id_of_nearest(df1, key=["x", "y"], df2=df2)
    assert all(list(ids) == np.asarray([0, 2, 1, 3]))


    # looking for closest in the same dataset
    ids = dili.find_id_of_nearest(df1, key=["x", "y"])
    assert all(list(ids) == np.asarray([1, 0, 3, 2]))


def main():
    unittest.main()
