# /usr/bin/env python
# -*- coding: utf-8 -*-

from loguru import logger
import pyqtgraph
from typing import List, cast
import ast
from pyqtgraph.parametertree import ParameterTree
import pyqtgraph.parametertree.parameterTypes as pTypes
import collections
import numpy as np
from typing import Union


def params_and_values(
    p: pyqtgraph.parametertree.Parameter, pth=None, dct=None, separator: str = ";"
):
    """
    Get dict of all parameters. Key is the path to the parameter, value is value of the parameter.
    :param p:
    :param pth:
    :param dct:
    :param separator:  default ";"
    :return:
    """
    if dct is None:
        dct = {}
    for name in p.getValues():
        # print(f"name: {name}, type {type(name)}")
        if pth is not None:
            pth_local = pth + separator + name
        else:
            pth_local = name
        # print(pth)
        ch = p.child(name)
        # print(f"name: {name}, type {type(ch)}")
        if type(ch) is pyqtgraph.parametertree.parameterTypes.SimpleParameter:
            dct[pth_local] = ch.value()
            # print(pth)
        else:
            params_and_values(ch, pth_local, dct=dct)

    return dct


def find_parameter_path_by_fragment(
    p: pyqtgraph.parametertree.Parameter, fragment, pth=None, dct=None, separator=";"
):
    """
    Get list of paths of all parameters where path contain a fragment.
    :param p: pyqtgraph.parametertree.Parameter
    :param fragment: fragment of path containing whole path parts separated by separator. E.g. "part2;part3"
    :param pth:
    :param dct: usefull for recursive call
    :param separator:  default ";"
    :return: list of paths
    """
    if dct is None:
        dct = {}

    pav = params_and_values(p, pth=pth, dct=dct, separator=separator)

    params = set()
    for param_pth in pav.keys():
        fnd = param_pth.find(fragment)
        if fnd >= 0:
            # check if it is begining of parameter name
            if (fnd == 0) or (param_pth[fnd - 1] == separator):
                fnd += len(fragment)
                # check the end of fragment
                if (fnd == (len(param_pth))) or (param_pth[fnd] == separator):
                    params.add(param_pth[:fnd])
    return list(params)

    # for name in p.getValues():
    #     # print(f"name: {name}, type {type(name)}")
    #     if pth is not None:
    #         pth_local = pth + separator + name
    #     else:
    #         pth_local = name
    #     # print(pth)
    #     ch = p.child(name)
    #     # print(f"name: {name}, type {type(ch)}")
    #     if type(ch) is pyqtgraph.parametertree.parameterTypes.SimpleParameter:
    #         dct[pth_local] = ch.value()
    #         # print(pth)
    #     else:
    #         params_and_values(ch, pth_local)
    #
    # return dct


def set_parameters_by_path(
    parameters: pyqtgraph.parametertree.Parameter,
    path_val_couple_list: List,
    parse_path=True,
    separator=";",
    literal_eval=False
):
    """
    Set value to parameter.
    :param parameters: paramtree.Paramterr
    :param path_val_couple_list: list of couple [Path to parameter can be separated by ";", value]
    :param value:
    :param parse_path: Turn on separation of path by separator
    :param separator: separator to separate parts of path. Default is ";"
    :return:
    """

    for param_path, param_value in path_val_couple_list:
        value = param_value
        set_parameter_by_path(
            parameters,
            param_path,
            value=value,
            parse_path=parse_path,
            separator=separator,
            literal_eval=literal_eval
        )


def set_parameter_by_path(
    parameters: pyqtgraph.parametertree.Parameter,
    param_path: str,
    value,
    parse_path=True,
    separator=";",
    literal_eval:bool=False
):
    """
    Set value to parameter.
    :param param_path: Path to parameter can be separated by ";"
    :param value:
    :param parse_path: Turn on separation of path by ";"
    :return:
    """
    if literal_eval and type(value) is str:
        value = ast.literal_eval(value)
    logger.debug(f"param path={param_path}, ast value={value}")
    p = get_parameter_by_path(
        parameters=parameters,
        param_path=param_path,
        parse_path=parse_path,
        separator=separator,
    )
    p.setValue(value)


def get_parameter_by_path(
    parameters: pyqtgraph.parametertree.Parameter,
    # param_path: Union[str, List[str]],
    param_path: str,
    parse_path=True,
    separator=";",
):

    """
    Get parameter based path to parameter.

    :param separator:
    :param param_path: Path to parameter can be separated by ";"
    :param value:
    :param parse_path: Turn on separation of path by ";"
    :return:
    """
    logger.debug(f"Get {param_path}")


    param_path_list: List
    if parse_path:
        param_path_list = param_path.split(separator)
    else:
        param_path_list = [param_path]
    fnparam = parameters.param(*param_path_list)
    return fnparam


def to_pyqtgraph_struct(name, value, opts: dict = None):
    """
    Prepare structure for creating pyqtgraph tree.
    :param name:
    :param value: simple-structured list or dict which should be converted to pyqtgraph-like struct
    :param opts:
    :return: pyqtgraph_struct useful which can be converted to params by Parameter(pg_struct)
    """
    if opts is None:
        opts = {}
    if "type" in opts:
        tp = opts["type"]
    else:
        tp = value.__class__.__name__

    if tp in (
        "list",
        "ndarray",
        "OrderedDict",
        "dict",
        "int",
        "float",
        "bool",
        "str",
        "color",
        "colormap",
    ):
        pass
    else:
        # some custome object
        return value
    item_properties = {
        "name": name,
        "value": value,
        "type": tp,
    }
    # if key in params.keys():

    children_properties = {}
    if "children" in opts.keys():
        children_properties = opts.pop("children")
    item_properties.update(opts)
    item_properties["reconstruction_type"] = tp

    if tp in ("list", "ndarray", "OrderedDict", "dict"):

        # key_parameters['type'] = key_parameters['type']
        item_properties["type"] = "group"
        item_properties.pop("value")
        if tp == "list":
            children_key_value = collections.OrderedDict(
                zip(map(str, range(len(value))), value)
            )
        elif tp == "ndarray":
            value_list = value.to_list()
            children_key_value = collections.OrderedDict(
                zip(map(str, range(len(value_list))), value_list)
            )
        elif tp in ("dict", "OrderedDict"):
            children_key_value = value

        children_list = []
        for keyi, vali in children_key_value.items():
            children_properties_i: dict = {}
            if keyi in children_properties:
                children_properties_i.update(children_properties[keyi])
            children_item = to_pyqtgraph_struct(keyi, vali, children_properties_i)
            children_list.append(children_item)

        item_properties["children"] = children_list

        # value = value_list
        # logger.debug(key_parameters)
    return item_properties


def from_pyqtgraph_struct(dct):
    """
    Get simple structured dict from pyqtgraph params saveState() export.

    :param dct: dct = parameters.saveState()
    :return:
    """
    output = {}
    key = dct["name"]
    if "children" in dct.keys():
        reconstruction_type = "dict"

        if "reconstruction_type" in dct.keys():
            reconstruction_type = dct["reconstruction_type"]

        if reconstruction_type in ("list", "ndarray"):
            children_list = []
            for child in dct["children"]:
                if reconstruction_type == "dict":
                    child_item = dct["children"][child]  # ok for line 214
                elif type(dct["children"]) is collections.OrderedDict:
                    child_item = dct["children"][child]  # ok for line 214 and type
                else:
                    child_item = child
                keyi, valuei = from_pyqtgraph_struct(child_item)
                children_list.append(valuei)
            value = children_list

        elif reconstruction_type in ("dict", "OrderedDict"):
            children_dict = {}
            for child in dct["children"]:
                if reconstruction_type == "OrderedDict":
                    if type(dct["children"]) is list:
                        child_item = child
                    else:
                        child_item = dct["children"][child]  # ok for line 214 and type
                else:
                    if type(dct["children"]) is collections.OrderedDict:
                        child_item = dct["children"][child]  # ok for line 214 and type
                    else:
                        child_item = child
                keyi, valuei = from_pyqtgraph_struct(child_item)
                children_dict[keyi] = valuei
            value = children_dict

    else:
        value = dct["value"]

    return key, value


# def find_in_structure(structure, key=None, value=None):
#     if type(structure) == list:
#         for i in range(0, len(structure)):
#             find_in_structure(structure[i])
#
#     elif type(structure) == dict:
#         for keyi in structure:
#             if key is not None and key == keyi:
#                 if structure[key] == value:
#                     return structure
#
#             fnd = find_in_structure()


class ListParameter(pTypes.GroupParameter):
    """
    New keywords

    titles: is list of titles
    value: list of values
    """

    def __init__(self, **opts):
        values = opts.pop("value")
        parent_opts = {"name": opts.pop("name"), "type": "bool", "value": values}
        if "title" in opts.keys():
            parent_opts["title"] = opts.pop("title")
        if "reconstruction_type" in opts.keys():
            parent_opts["reconstruction_type"] = opts.pop("reconstruction_type")
        # opts['type'] = 'bool'
        # opts['value'] = True
        pTypes.GroupParameter.__init__(self, **parent_opts)
        # gp = pTypes.GroupParameter(name=opts['name'], title=opts['title'])
        if "names" in opts.keys():
            names = opts["names"]
        else:
            names = list(map(str, range(len(values))))

        for i in range(len(values)):
            opts["name"] = names[i]
            opts["value"] = values[i]
            self.addChild(opts)

        for child in self.childs:
            child.sigValueChanged.connect(self.valuesChanged)

        self.sigValueChanged.connect(self.valueChanged)

    def valuesChanged(self):
        new_val = []
        for i in range(len(self.childs)):
            new_val.append(self.childs[i].value())

        self.setValue(new_val)

    def valueChanged(self):
        new_val = self.value()
        for i in range(len(self.childs)):
            self.childs[i].setValue(new_val[i])


class AreaSamplingParameter(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts["type"] = "bool"
        opts["value"] = True
        voxelsize_mm = [1.0, 1.0, 1.0]
        areasize_mm = [100.0, 100.0, 100.0]
        areasize_px = [100, 100, 100]

        if "voxelsize_mm" in opts.keys():
            voxelsize_mm = opts.pop("voxelsize_mm")
        if "areasize_mm" in opts.keys():
            areasize_mm = opts.pop("areasize_mm")
        if "areasize_px" in opts.keys():
            areasize_px = opts.pop("areasize_px")

        pTypes.GroupParameter.__init__(self, **opts)

        self.p_voxelsize_mm = ListParameter(
            name="voxelsize_mm",
            value=voxelsize_mm,
            type="float",
            suffix="mm",
            siPrefix=False,
            reconstruction_type="list",
        )
        self.p_areasize_px = ListParameter(
            name="areasize_px",
            value=areasize_px,
            type="int",
            suffix="px",
            siPrefix=False,
            reconstruction_type="list",
        )
        self.p_areasize_mm = ListParameter(
            name="areasize_mm",
            value=areasize_mm,
            type="float",
            suffix="mm",
            siPrefix=False,
            reconstruction_type="list",
        )

        self.addChild(self.p_voxelsize_mm)
        self.addChild(self.p_areasize_mm)
        self.addChild(self.p_areasize_px)

        self.p_areasize_mm.sigValueChanged.connect(self.areasize_mChanged)
        self.p_areasize_px.sigValueChanged.connect(self.areasize_pxChanged)

    def areasize_mChanged(self):
        as_m = np.asarray(self.p_areasize_mm.value())
        vs_m = np.asarray(self.p_voxelsize_mm.value()).astype(np.float)
        val = (as_m / vs_m).astype(np.int).tolist()
        self.p_areasize_px.setValue(val, blockSignal=self.areasize_pxChanged)

    def areasize_pxChanged(self):
        val = (
            np.asarray(self.p_voxelsize_mm.value())
            * np.asarray(self.p_areasize_px.value())
        ).tolist()
        self.p_areasize_mm.setValue(val, blockSignal=self.areasize_mChanged)

    def voxelsizeChanged(self):
        self.z_size_px.setValue(
            int(self.z_size_m.value() / self.z_m.value()),
            blockSignal=self.z_size_pxChanged,
        )

    # def z_mChanged(self):
    #     self.z_.setValue(1.0 / self.a.value(), blockSignal=self.bChanged)
    def z_size_mChanged(self):
        self.z_size_px.setValue(
            int(self.z_size_m.value() / self.z_m.value()),
            blockSignal=self.z_size_pxChanged,
        )

    def z_size_pxChanged(self):
        self.z_size_m.setValue(
            int(self.z_size_px.value() * self.z_m.value()),
            blockSignal=self.z_size_mChanged,
        )

        # def aChanged(self):
        #     self.b.setValue(1.0 / self.a.value(), blockSignal=self.bChanged)
        #
        # def bChanged(self):
        #     self.a.setValue(1.0 / self.b.value(), blockSignal=self.aChanged)


## test add/remove
## this group includes a menu allowing the user to add new parameters into its child list
class ScalableGroup(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts["type"] = "group"
        opts["addText"] = "Add"
        opts["addList"] = ["str", "float", "int"]
        pTypes.GroupParameter.__init__(self, **opts)

    def addNew(self, typ):
        val = {"str": "", "float": 0.0, "int": 0}[typ]
        self.addChild(
            dict(
                name="ScalableParam %d" % (len(self.childs) + 1),
                type=typ,
                value=val,
                removable=True,
                renamable=True,
            )
        )


class BatchFileProcessingParameter(pTypes.GroupParameter):
    def __init__(self, **opts):
        opts["type"] = "group"
        opts["addText"] = "Add"
        {"name": "Save State", "type": "action"},
        # opts['addList'] = ['str', 'float', 'int']
        pTypes.GroupParameter.__init__(self, **opts)

    def addNew(self):
        # val = {
        #     'str': '',
        #     'float': 0.0,
        #     'int': 0
        # }[typ]
        from PyQt5 import QtWidgets

        fname = QtWidgets.QFileDialog.getOpenFileName(None, "Open file", "")[0]


def add_tip(struct, name, tip):
    from imma import dili

    pth, objstr = dili.find_in_struct(struct, name)
    obj = dili.pick_from_struct(struct, pth[:-1])
    obj["tip"] = tip


def add_tips(struct, names_tips):
    """
    :param struct:
    :param names_tips:  dict with name of property and tip
    :return:
    """
    for key in names_tips:
        add_tip(struct, key, names_tips[key])
