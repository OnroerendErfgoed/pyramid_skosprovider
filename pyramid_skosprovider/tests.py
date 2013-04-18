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

from skosprovider.skos import (
    Concept
)

try:
    import unittest2 as unittest
except ImportError:
    import unittest

larch = {
    'id': 1,
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'The Larch'},
        {'type': 'prefLabel', 'language': 'nl', 'label': 'De Lariks'}
    ],
    'notes': [
        {'type': 'definition', 'language': 'en', 'note': 'A type of tree.'}
    ]
}

chestnut = {
    'id': 2,
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'The Chestnut'},
        {'type': 'altLabel', 'language': 'nl', 'label': 'De Paardekastanje'}
    ],
    'notes': [
        {
            'type': 'definition', 'language': 'en',
            'note': 'A different type of tree.'
        }
    ]
}

species = {
    'id': 3,
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'Trees by species'},
        {'type': 'prefLabel', 'language': 'nl', 'label': 'Bomen per soort'}
    ],
    'type': 'collection',
    'members': ['1', '2']
}

trees = FlatDictionaryProvider(
    {'id': 'TREES', 'default_language': 'nl'},
    [larch, chestnut, species]
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
        self.regis = self.config.get_skos_registry()
        self.regis.register_provider(trees)

    def tearDown(self):
        testing.tearDown()
        del self.config
        del self.regis

    def _get_dummy_request(self, *args, **kwargs):
        request = testing.DummyRequest(*args, **kwargs)
        request.skos_registry = self.regis
        return request

    def _get_provider_view(self, request):
        from pyramid_skosprovider.views import ProviderView
        return ProviderView(request)

    def test_get_conceptschemes(self):
        request = self._get_dummy_request()
        pv = self._get_provider_view(request)
        conceptschemes = pv.get_conceptschemes()
        self.assertIsInstance(conceptschemes, list)
        for cs in conceptschemes:
            self.assertIsInstance(cs, dict)
            self.assertIn('id', cs)

    def test_get_conceptscheme(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        cs = pv.get_conceptscheme()
        self.assertEqual({'id': 'TREES'}, cs)

    def test_get_unexisting_conceptscheme(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'PARROTS'}
        pv = self._get_provider_view(request)
        cs = pv.get_conceptscheme()
        self.assertIsInstance(cs, HTTPNotFound)

    def test_get_conceptscheme_concepts(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(3, len(concepts))
        for c in concepts:
            self.assertIsInstance(c, dict)
            self.assertIn('id', c)

    def test_get_conceptscheme_concepts_complete_range(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'TREES'}
        request.headers['Range'] = 'items=0-19'
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertEqual(3, len(concepts))

    def test_get_conceptscheme_concepts_partial_range(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'TREES'}
        request.headers['Range'] = 'items=0-0'
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertEqual(1, len(concepts))

    def test_get_unexisting_conceptscheme_concepts(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'PARROTS'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, HTTPNotFound)

    def test_get_conceptscheme_concepts_search_label(self):
        request = self._get_dummy_request({
            'label': 'Larc'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(1, len(concepts))
        self.assertEqual(1, concepts[0]['id'])

    def test_get_conceptscheme_concepts_search_type_concept(self):
        request = self._get_dummy_request({
            'type': 'concept'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(2, len(concepts))

    def test_get_conceptscheme_concepts_search_type_collection(self):
        request = self._get_dummy_request({
            'type': 'collection'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(1, len(concepts))

    def test_get_conceptscheme_concepts_search_in_collection(self):
        request = self._get_dummy_request({
            'collection': 3
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(2, len(concepts))

    def test_get_concept(self):
        request = self._get_dummy_request()
        request.matchdict = {
            'scheme_id': 'TREES', 
            'concept_id': 1
        }
        pv = self._get_provider_view(request)
        concept = pv.get_concept()
        self.assertIsInstance(concept, Concept)
        self.assertIn('id', concept)
        self.assertEqual(1, concept['id'])

    def test_get_unexsisting_concept(self):
        request = self._get_dummy_request()
        request.matchdict = {
            'scheme_id': 'TREES', 
            'concept_id': 123456789
        }
        pv = self._get_provider_view(request)
        concept = pv.get_concept()
        self.assertIsInstance(concept, HTTPNotFound)


class TestUtils(unittest.TestCase):

    def test_parse_range_header(self):
        from pyramid_skosprovider.utils import parse_range_header
        headers = [
            {
                'header': 'items=0-19',
                'result': {
                    'start': 0,
                    'number': 20,
                    'finish': 19
                }
            }, {
                'header': 'items:0-19',
                'result': False
            }, {
                'header': 'test',
                'result': False
            }, {
                'header': 'items=t-t',
                'result': False
            }, {
                'header': 'items=10-0',
                'result': {
                    'start': 10,
                    'finish': 10,
                    'number': 1
                }
            }]
        for header in headers:
            res = parse_range_header(header['header'])
            self.assertEqual(res, header['result'])
