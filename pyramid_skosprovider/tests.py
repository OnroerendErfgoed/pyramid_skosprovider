# -*- coding: utf8 -*-

from pyramid import testing

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound
    )

from pyramid_skosprovider import (
    ISkosRegistry,
    _build_skos_registry,
    get_skos_registry,
    includeme
)

from skosprovider.registry import (
    Registry
)

from skosprovider.providers import (
    FlatDictionaryProvider
)

try:
    import unittest2 as unittest
except ImportError:
    import unittest

larch = {
    'id': 1,
    'labels': [
        {'type': 'pref', 'lang': 'en', 'label': 'The Larch'},
        {'type': 'pref', 'lang': 'nl', 'label': 'De Lariks'}
    ],
    'notes': [
        {'type': 'definition', 'lang': 'en', 'note': 'A type of tree.'}
    ]
}

chestnut = {
    'id': 2,
    'labels': [
        {'type': 'pref', 'lang': 'en', 'label': 'The Chestnut'},
        {'type': 'alt', 'lang': 'nl', 'label': 'De Paardekastanje'}
    ],
    'notes': [
        {
            'type': 'definition', 'lang': 'en',
            'note': 'A different type of tree.'
        }
    ]
}

trees = FlatDictionaryProvider(
    {'id': 'TREES', 'default_language': 'nl'},
    [larch, chestnut]
)


class TestRegistry(object):

    def __init__(self, settings=None):

        if settings is None:
            self.settings = {}
        else:
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


class ProviderViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_skosprovider')
        regis = self.config.get_skos_registry()
        regis.register_provider(trees)

    def tearDown(self):
        testing.tearDown()

    def _get_provider_view(self, request):
        from pyramid_skosprovider.views import ProviderView
        return ProviderView(request)

    def test_get_conceptschemes(self):
        request = testing.DummyRequest()
        pv = self._get_provider_view(request)
        conceptschemes = pv.get_conceptschemes()
        self.assertIsInstance(conceptschemes, list)
        for cs in conceptschemes:
            self.assertIsInstance(cs, dict)
            self.assertIn('id', cs)

    def test_get_conceptscheme(self):
        request = testing.DummyRequest()
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        cs = pv.get_conceptscheme()
        self.assertEqual({'id': 'TREES'}, cs)

    def test_get_unexisting_conceptscheme(self):
        request = testing.DummyRequest()
        request.matchdict = {'scheme_id': 'PARROTS'}
        pv = self._get_provider_view(request)
        cs = pv.get_conceptscheme()
        self.assertIsInstance(cs, HTTPNotFound)

    def test_get_conceptscheme_concepts(self):
        request = testing.DummyRequest()
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        for c in concepts:
            self.assertIsInstance(c, dict)
            self.assertIn('id', c)

    def test_get_unexisting_conceptscheme_concepts(self):
        request = testing.DummyRequest()
        request.matchdict = {'scheme_id': 'PARROTS'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, HTTPNotFound)

    def test_get_concept(self):
        request = testing.DummyRequest()
        request.matchdict = {
            'scheme_id': 'TREES', 
            'concept_id': 1
        }
        pv = self._get_provider_view(request)
        concept = pv.get_concept()
        self.assertIsInstance(concept, dict)
        self.assertIn('id', concept)
        self.assertEqual(1, concept['id'])

    def test_get_unexsisting_concept(self):
        request = testing.DummyRequest()
        request.matchdict = {
            'scheme_id': 'TREES', 
            'concept_id': 123456789
        }
        pv = self._get_provider_view(request)
        concept = pv.get_concept()
        self.assertIsInstance(concept, HTTPNotFound)
