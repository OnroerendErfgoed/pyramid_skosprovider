# -*- coding: utf8 -*-

from __future__ import unicode_literals

from pyramid import testing

from pyramid_skosprovider import (
    ISkosRegistry,
    get_global_skos_registry,
    get_request_skos_registry,
    _register_global_skos_registry,
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


def _skosregis_factory_global():
    return Registry(
        instance_scope='threaded_global'
    )


def _skosregis_factory_request(request):
    return Registry(
        instance_scope='threaded_thread'
    )


class TestGetAndBuild(unittest.TestCase):

    def test_get_global_skos_registry(self):
        r = TestRegistry()
        SR = Registry(
            instance_scope='threaded_global'
        )
        r.registerUtility(SR, ISkosRegistry)
        SR2 = get_global_skos_registry(r)
        self.assertEqual(SR, SR2)

    def test_register_global_skos_registry_custom_factory(self):
        r = TestRegistry()
        settings={
            'skosregistry_location': 'registry',
            'skosregistry_factory': 'tests.test_varia._skosregis_factory_global'
        };
        SR = _register_global_skos_registry(r, settings)
        self.assertIsInstance(SR, Registry)

    def test_register_global_skos_registry_already_exists(self):
        r = TestRegistry()
        SR = Registry(
            instance_scope='threaded_global'
        )
        r.registerUtility(SR, ISkosRegistry)
        SR2 = _register_global_skos_registry(r, {})
        self.assertEqual(SR, SR2)

    def test_register_global_skos_registry_default_settings(self):
        r = TestRegistry()
        SR = _register_global_skos_registry(r, {})
        self.assertIsInstance(SR, Registry)

    def test_get_request_skos_registry(self):
        request = testing.DummyRequest()
        request.registry.settings = {'skosprovider.skosregistry_location': 'request'}
        SR = get_request_skos_registry(request)
        self.assertIsInstance(SR, Registry)

    def test_get_request_skos_registry_custom_factory(self):
        request = testing.DummyRequest()
        request.registry.settings = {
            'skosprovider.skosregistry_location': 'request',
            'skosprovider.skosregistry_factory': 'tests.test_varia._skosregis_factory_request'
        }
        SR = get_request_skos_registry(request)
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

    def test_includeme_request(self):
        settings = {
            'skosprovider.skosregistry_location': 'request',
            'skosprovider.skosregistry_factory': 'tests.test_varia._skosregis_factory_request'
        }
        self.config = testing.setUp(settings=settings);
        includeme(self.config)
