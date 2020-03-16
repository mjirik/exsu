# /usr/bin/env python
# -*- coding: utf-8 -*-

import loguru
import exsu.packages


def test_package_version():
    dct = exsu.packages.get_version_of_packages_as_dict(["numpy", "scipy"])

    assert "numpy_version" in dct
    assert "scipy_version" in dct
