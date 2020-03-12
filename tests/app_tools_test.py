#! /usr/bin/python
# -*- coding: utf-8 -*-

from loguru import logger


from exsu import app_tools

def test_icon():
    app_tools.create_icon("MyApp", "fn.ico", conda_env_name="super_env")
