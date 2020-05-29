#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module is provides funcions for dict lists and functions processing
"""
from loguru import logger
import collections
import inspect
import copy
import numpy as np

import sys
from collections import Mapping, Set, Sequence

# dual python 2/3 compatability, inspired by the "six" library
string_types = (str) if str is bytes else (str, bytes)
iteritems = lambda mapping: getattr(mapping, "iteritems", mapping.items)()


def get_default_kwargs(obj):
    if "__init__" in dir(obj):
        if inspect.isfunction(obj.__init__) or inspect.ismethod(obj.__init__):
            argspec = inspect.getfullargspec(obj.__init__)
        else:
            argspec = inspect.getfullargspec(obj)
    else:
        argspec = inspect.getfullargspec(obj)

    dif = len(argspec.args) - len(argspec.defaults)
    args = argspec.args[dif:]
    defaults = argspec.defaults
    # args = argspec.args[1:]
    # defaults = argspec.defaults
    dc = collections.OrderedDict(zip(args, defaults))
    return dc


def subdict(dct, keys):
    if type(dct) == collections.OrderedDict:
        p = collections.OrderedDict()
    else:
        p = {}
    for key, value in dct.items():
        if key in keys:
            p[key] = value
    # p = {key: value for key, value in dct.items() if key in keys}
    return p


def list_filter(
    lst, startswith=None, notstartswith=None, contain=None, notcontain=None
):
    """ Keep in list items according to filter parameters.

    :param lst: item list
    :param startswith: keep items starting with
    :param notstartswith: remove items starting with
    :return:
    """
    keeped = []
    for item in lst:
        keep = False
        if startswith is not None:
            if item.startswith(startswith):
                keep = True
        if notstartswith is not None:
            if not item.startswith(notstartswith):
                keep = True
        if contain is not None:
            if contain in item:
                keep = True
        if notcontain is not None:
            if not notcontain in item:
                keep = True

        if keep:
            keeped.append(item)
    return keeped


def kick_from_dict(dct, keys):
    if type(dct) == collections.OrderedDict:
        p = collections.OrderedDict()
    else:
        p = {}
    for key, value in dct.items():
        if key not in keys:
            p[key] = value

    # p = {key: value for key, value in dct.items() if key not in keys}
    return p


def split_dict(dct, keys):
    """
    Split dict into two subdicts based on keys.

    :param dct:
    :param keys:
    :return: dict_in, dict_out
    """
    if type(dct) == collections.OrderedDict:
        dict_in = collections.OrderedDict()
        dict_out = collections.OrderedDict()
    else:
        dict_in = {}
        dict_out = {}

    for key, value in dct.items():
        if key in keys:
            dict_in[key] = value
        else:
            dict_out[key] = value
    return dict_in, dict_out


def recursive_update(d, u):
    """
    Dict recursive update.



    Based on Alex Martelli code on stackoverflow
    http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth?answertab=votes#tab-top

    :param d: dict to update
    :param u: dict with same structure as d and new data
    :return:
    """
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = recursive_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


import collections
from operator import add

_FLAG_FIRST = object()


def flatten_dict_join_keys(dct, join_symbol=" ", simplify_iterables=False):
    """ Flatten dict with defined key join symbol.

    :param dct: dict to flatten
    :param join_symbol: default value is " "
    :param simplify_iterables: each element of lists and ndarrays is represented as one key
    :return:
    """
    if simplify_iterables:
        dct = ndarray_to_list_in_structure(dct)
        dct = list_to_dict_in_structure(dct, keys_to_str=True)
    return dict(flatten_dict(dct, join=lambda a, b: a + join_symbol + b))


def flatten_dict(dct, separator=None, join=add, lift=lambda x: x):
    """

    Based on ninjagecko code on stackoveflow
    http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys

    :param dct: dict to flatten
    :param separator: use preset values for join and lift.
    Use empty list or tuple [], () for key hierarchy stored in list.
    If simple_mode is string it is used as a separator.
    :param join: join operation. To join keys with '_' use join=lambda a,b:a+'_'+b
    :param lift:  to have all hierarchy keys in lise use lift=lambda x:(x,))
    :return:

    For all keys from above hierarchy in list use:
    dict( flattenDict(testData, lift=lambda x:(x,)) )

    For all keys from abve hierarchy separated by '_' use:
    dict( flattenDict(testData, join=lambda a,b:a+'_'+b) )
    """

    if type(separator) is str:
        join = lambda a, b: a + separator + b
    elif type(separator) in (list, tuple):
        lift = lambda x: (x,)

    results = []

    def visit(subdict, results, partialKey):
        for k, v in subdict.items():
            newKey = lift(k) if partialKey == _FLAG_FIRST else join(partialKey, lift(k))
            if isinstance(v, collections.Mapping):
                visit(v, results, newKey)
            else:
                results.append((newKey, v))

    visit(dct, results, _FLAG_FIRST)
    return results


def list_contains(list_of_strings, substring, return_true_false_array=False):
    """ Get strings in list which contains substring.

    """
    key_tf = [keyi.find(substring) != -1 for keyi in list_of_strings]
    if return_true_false_array:
        return key_tf
    from itertools import compress

    keys_to_remove = list(compress(list_of_strings, key_tf))
    return keys_to_remove


def df_drop_keys_contains(df, ignore_key_pattern="time"):
    """
    Return dataframe columns keys without columns containing key pattern.
    :param df:
    :param ignore_key_pattern:
    :return:
    """

    keys_to_remove = list_contains(df.keys(), ignore_key_pattern)
    # key_tf = [key.find(noinfo_key_pattern) != -1 for key in df.keys()]
    # keys_to_remove
    # remove duplicates
    ks = copy.copy(list(df.keys()))
    for key in keys_to_remove:
        ks.remove(key)

    return ks


def df_drop_duplicates(df, ignore_key_pattern="time"):
    """
    Drop duplicates from dataframe ignore columns with keys containing defined pattern.

    :param df:
    :param noinfo_key_pattern:
    :return:
    """

    ks = df_drop_keys_contains(df, ignore_key_pattern)

    df = df.drop_duplicates(ks)
    return df


def ndarray_to_list_in_structure(item, squeeze=True):
    """ Change ndarray in structure of lists and dicts into lists. Recursive.
    """
    tp = type(item)

    if tp == np.ndarray:
        if squeeze:
            item = item.squeeze()
        item = item.tolist()
    elif tp == list:
        for i in range(len(item)):
            item[i] = ndarray_to_list_in_structure(item[i])
    elif tp == dict:
        for lab in item:
            item[lab] = ndarray_to_list_in_structure(item[lab])

    return item

def list_to_dict_in_structure(item, keys_to_str=False):
    """ Change ndarray in structure of lists and dicts into lists. Recursive.
    :param item: list or dict
    """
    tp = type(item)

    if tp == list:
        item = {
            str(key) if keys_to_str else key:
                list_to_dict_in_structure(value, keys_to_str=keys_to_str) for key, value in enumerate(item)
        }
        # for i in range(len(item)):
        #     item[i] = ndarray_to_list_in_structure(item[i])
    elif tp == dict:
        for lab in item:
            item[lab] = list_to_dict_in_structure(item[lab], keys_to_str=keys_to_str)

    return item


def dict_find_key(dd, value):
    """ Find first suitable key in dict.

    :param dd:
    :param value:
    :return:
    """
    key = next(key for key, val in dd.items() if val == value)
    return key


def sort_list_of_dicts(lst_of_dct, keys, reverse=False, **sort_args):
    """
    Sort list of dicts by one or multiple keys.

    If the key is not available, sort these to the end.

    :param lst_of_dct: input structure. List of dicts.
    :param keys: one or more keys in list
    :param reverse:
    :param sort_args:
    :return:
    """

    if type(keys) != list:
        keys = [keys]
    # dcmdir = lst_of_dct[:]
    # lst_of_dct.sort(key=lambda x: [x[key] for key in keys], reverse=reverse, **sort_args)
    lst_of_dct.sort(
        key=lambda x: [((False, x[key]) if key in x else (True, 0)) for key in keys],
        reverse=reverse,
        **sort_args
    )
    return lst_of_dct


def ordered_dict_to_dict(config):
    """
    Use dict instead of ordered dict in structure.
    """

    if type(config) == collections.OrderedDict:
        config = dict(config)
    if type(config) == list:
        for i in range(0, len(config)):
            config[i] = ordered_dict_to_dict(config[i])
    elif type(config) == dict:
        for key in config:
            config[key] = ordered_dict_to_dict(config[key])

    return config


def find_in_list_of_lists(list_of_lists, value):
    """
    Find value in list of lists and return first found index of list.
    :param list_of_lists:
    :param value:
    :return:
    """
    for i, lst in enumerate(list_of_lists):
        if value in lst:
            return i
    return None


# def struct_to_yaml(cfg):
#     """
#     write complex struct with dicts and lists into yaml
#     :param cfg:
#     :return:
#     """
#     import yaml
#     # convert values to json
#     isconverted = {}
#     for key, value in cfg.iteritems():
#         if type(value) in (str, int, float, bool):
#
#             isconverted[key] = False
#             if type(value) is str:
#                 pass
#
#         else:
#             isconverted[key] = True
#             cfg[key] = yaml.dump(value, default_flow_style=True)
#     return cfg


def objwalk(obj, path=(), memo=None):
    if memo is None:
        memo = set()
    iterator = None
    if isinstance(obj, Mapping):
        iterator = iteritems
    elif isinstance(obj, (Sequence, Set)) and not isinstance(obj, string_types):
        iterator = enumerate
    if iterator:
        if id(obj) not in memo:
            memo.add(id(obj))
            for path_component, value in iterator(obj):
                for result in objwalk(value, path + (path_component,), memo):
                    yield result
            memo.remove(id(obj))
    else:
        yield path, obj


def find_value_in_struct(structure, value):
    for pth, obj in objwalk(structure):
        # a.append([type(pth), pth])
        if obj == value:
            return pth, obj


def find_in_struct(structure, keys):
    """
    Find and return path to first existing key.

    Allways return the path to the deepest possible key.

    :param structure: structure of lists or dicts.
    :param keys: one or more keys. The order of keys is irrelevant.
    :return: 
    """
    if type(keys) in (list, tuple):
        pass
    else:
        keys = [keys]
    for pth, obj in objwalk(structure):
        # a.append([type(pth), pth])
        all_keys_found = True
        for key in keys:
            if key in pth:
                pass
            else:
                all_keys_found = False
        if all_keys_found:
            return list(pth)


def set_in_struct(structure, pth, val):
    struct = structure
    for pthi in pth[:-1]:
        struct = struct[pthi]
    struct[pth[-1]] = val


def pick_from_struct(structure, pth):
    struct = structure
    for pthi in pth:
        struct = struct[pthi]
    return struct


def find_id_of_nearest(df1, key, df2=None, key2=None):
    """
    Find closest points in dataframe. The axis of the space ar given by keys

    :param df1: pandas.dataframe
    :param key: one or more keys in list describing the axis
    :param key2:
    :param df2:
    :return:
    """
    if key2 is None:
        key2 = key

    if df2 is None:
        df2 = df1

    inds = np.zeros(len(df1), dtype=int)
    for i in range(len(df1)):
        norm_i = np.linalg.norm(np.asarray(df1[key].values - df2.iloc[i][key2].values, dtype=float), axis=1)
        if df1 is df2:
            norm_i[i] = None
        inds[i] = np.nanargmin(norm_i)
    return inds

