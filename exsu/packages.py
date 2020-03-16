# /usr/bin/env python
# -*- coding: utf-8 -*-

import loguru


def get_version_of_packages(modules):
    return [getattr(__import__(module_str), "__version__") for module_str in modules]


def get_version_of_packages_as_dict(modules, col_str_pattern="{module}_version"):
    versions = get_version_of_packages(modules)
    col_names = [col_str_pattern.format(module=module) for module in modules]
    return dict(zip(col_names, versions))
