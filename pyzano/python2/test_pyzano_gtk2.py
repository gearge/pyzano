#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import unittest
import os

import pygtk
pygtk.require('2.0')
import gtk  # pygtk.require() must be called before importing gtk

if os.sys.version_info < (2, 7):
    raise SystemExit("%s: error: unittest from python version 2.7 or newer required" % os.path.basename(os.sys.argv[0]))

