#!/usr/bin/env python

"""
@file ion/core/exception.py
@author Michael Meisinger
@brief tests for applications
"""

import os, sys

import ion.util.ionlog
log = ion.util.ionlog.getLogger(__name__)

from ion.core.pack.application import AppLoader, AppDefinition
from ion.test.iontest import IonTestCase
import ion.util.procutils as pu

class AppLoaderTest(IonTestCase):
    """
    Tests the app loader.
    """
    def test_load_appfile(self):
        # Tests run in <main>/_trial_temp
        filename = '../res/apps/example.app'
        app = AppLoader.load_app_definition(filename)
        log.debug(app)
        self.assertTrue(app)
        self.assertIsInstance(app, AppDefinition)
