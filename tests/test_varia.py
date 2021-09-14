# -*- coding: utf8 -*-

from pyramid import testing

from pyramid_skosprovider import (
    ISkosRegistry,
    get_skos_registry,
    _register_global_skos_registry,
    _register_request_skos_registry,
    includeme
)

from skosprovider.registry import (
    Registry
)

import unittest
import pytest


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

    def test_get_skos_registry(self):
        settings={
            'skosprovider.skosregistry_location': 'registry',
        }
        r = TestRegistry(settings=settings)
        SR = Registry(
            instance_scope='threaded_global'
        )
        r.registerUtility(SR, ISkosRegistry)
        SR2 = get_skos_registry(r)
        assert SR == SR2

    def test_get_skos_registry_not_working_for_requests(self):
        settings={
            'skosprovider.skosregistry_location': 'request',
        }
        r = TestRegistry(settings=settings)
        with pytest.raises(RuntimeError):
            assert isinstance(get_skos_registry(r), Registry)

    def test_register_global_skos_registry_custom_factory(self):
        settings={
            'skosprovider.skosregistry_location': 'registry',
            'skosprovider.skosregistry_factory': 'tests.test_varia._skosregis_factory_global'
        }
        r = TestRegistry(settings=settings)
        SR = _register_global_skos_registry(r)
        assert isinstance(SR, Registry)

    def test_register_global_skos_registry_already_exists(self):
        r = TestRegistry()
        SR = Registry(
            instance_scope='threaded_global'
        )
        r.registerUtility(SR, ISkosRegistry)
        SR2 = _register_global_skos_registry(r)
        assert isinstance(SR, Registry)

    def test_register_global_skos_registry_default_settings(self):
        r = TestRegistry()
        SR = _register_global_skos_registry(r)
        assert isinstance(SR, Registry)

    def test_get_request_skos_registry(self):
        request = testing.DummyRequest()
        request.registry.settings = {'skosprovider.skosregistry_location': 'request'}
        SR = _register_request_skos_registry(request)
        assert isinstance(SR, Registry)

    def test_get_request_skos_registry_custom_factory(self):
        request = testing.DummyRequest()
        request.registry.settings = {
            'skosprovider.skosregistry_location': 'request',
            'skosprovider.skosregistry_factory': 'tests.test_varia._skosregis_factory_request'
        }
        SR = _register_request_skos_registry(request)
        assert isinstance(SR, Registry)


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
