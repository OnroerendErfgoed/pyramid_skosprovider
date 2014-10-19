# -*- coding: utf8 -*-

from __future__ import unicode_literals

from pyramid import testing

from pyramid_skosprovider import (
    ISkosRegistry,
    _build_skos_registry,
    get_skos_registry,
    includeme
)

from skosprovider.registry import (
    Registry
)

import unittest


class TestRegistry(object):

    def __init__(self, settings=None):

        if settings is None:
            self.settings = {}
        else: # pragma NO COVER
            self.settings = settings 

        self.skos_registry = None

    def queryUtility(self, iface):
        return self.skos_registry

    def registerUtility(self, skos_registry, iface):
        self.skos_registry = skos_registry


class TestGetAndBuild(unittest.TestCase):

    def test_get_skos_registry(self):
        r = TestRegistry()
        SR = Registry()
        r.registerUtility(SR, ISkosRegistry)
        SR2 = get_skos_registry(r)
        self.assertEqual(SR, SR2)

    def test_build_skos_registry_already_exists(self):
        r = TestRegistry()
        SR = Registry()
        r.registerUtility(SR, ISkosRegistry)
        SR2 = _build_skos_registry(r)
        self.assertEqual(SR, SR2)

    def test_build_skos_registry_default_settings(self):
        r = TestRegistry()
        SR = _build_skos_registry(r)
        self.assertIsInstance(SR, Registry)


class TestIncludeMe(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        del self.config

    def test_includeme(self):
        includeme(self.config)
        SR = self.config.registry.queryUtility(ISkosRegistry)
        self.assertIsInstance(SR, Registry)

    def test_directive_was_added(self):
        includeme(self.config)
        SR = self.config.get_skos_registry()
        self.assertIsInstance(SR, Registry)
