# -*- coding: utf8 -*-

from __future__ import unicode_literals

from pyramid import testing

from pyramid.compat import (
    text_type
)

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound
)

from pyramid_skosprovider.tests import (
    larch,
    chestnut,
    species,
    trees
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

from skosprovider.skos import (
    Concept,
    Collection,
    Label,
    Note
)

import json

try:
    import unittest2 as unittest
except ImportError:
    import unittest


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

    def test_get_conceptscheme_concepts_search_dfs_all(self):
        request = self._get_dummy_request({
            'type': 'concept',
            'mode': 'dijitFilteringSelect',
            'label': '*'
        })
        request.matchdict = {
            'scheme_id': 'TREES'
        }
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(2, len(concepts))

    def test_get_conceptscheme_concepts_search_dfs_empty_label(self):
        request = self._get_dummy_request({
            'type': 'concept',
            'mode': 'dijitFilteringSelect',
            'label': ''
        })
        request.matchdict = {
            'scheme_id': 'TREES'
        }
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(0, len(concepts))

    def test_get_conceptscheme_concepts_search_dfs_label_star(self):
        request = self._get_dummy_request({
            'type': 'concept',
            'mode': 'dijitFilteringSelect',
            'label': 'De *'
        })
        request.matchdict = {
            'scheme_id': 'TREES'
        }
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(2, len(concepts))

    def test_get_conceptscheme_concepts_search_dfs_star_label(self):
        request = self._get_dummy_request({
            'type': 'concept',
            'mode': 'dijitFilteringSelect',
            'label': '*iks'
        })
        request.matchdict = {
            'scheme_id': 'TREES'
        }
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(1, len(concepts))

    def test_get_conceptscheme_concepts_search_dfs_star_label_star(self):
        request = self._get_dummy_request({
            'type': 'concept',
            'mode': 'dijitFilteringSelect',
            'label': '*Larik*'
        })
        request.matchdict = {
            'scheme_id': 'TREES'
        }
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(1, len(concepts))

    def test_get_concept(self):
        request = self._get_dummy_request()
        request.matchdict = {
            'scheme_id': 'TREES', 
            'c_id': 1
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
            'c_id': 123456789
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

    def _assert_is_labels(self, labels):
        self.assertIsInstance(labels, list)
        for l in labels:
            self.assertIsInstance(l, Label)

    def test_concept_adapter(self):
        from pyramid_skosprovider.utils import concept_adapter
        c = Concept(
            id=larch['id'],
            labels=larch['labels'],
            notes=larch['notes']
        )
        concept = concept_adapter(c,{})
        self.assertIsInstance(concept, dict)
        self.assertEqual(concept['id'], 1)
        self.assertIsInstance(concept['label'], text_type)
        self.assertIn(concept['type'], 'concept')
        self.assertEqual(len(concept['labels']), 2)
        self._assert_is_labels(concept['labels'])

    def test_collection_adapter(self):
        from pyramid_skosprovider.utils import collection_adapter
        c = Collection(
            id=species['id'],
            labels=species['labels'],
            members=species['members']
        )
        collection = collection_adapter(c,{})
        self.assertIsInstance(collection, dict)
        self.assertEqual(collection['id'], 3)
        self.assertIsInstance(collection['label'], text_type)
        self.assertIn('label', collection)
        self.assertEqual(collection['type'], 'collection')
        self.assertEqual(len(collection['labels']), 2)
        self._assert_is_labels(collection['labels'])

    def test_json_concept(self):
        from pyramid_skosprovider.utils import json_renderer
        c = Concept(
            id=larch['id'],
            labels=larch['labels'],
            notes=larch['notes']
        )
        r = json_renderer({})
        jsonstring = r(c, {})
        concept = json.loads(jsonstring)
        self.assertIsInstance(concept, dict)
        self.assertEqual(concept['id'], 1)
        self.assertIsInstance(concept['label'], text_type)
        self.assertEqual(concept['type'], 'concept')
        self.assertIsInstance(concept['labels'], list)
        self.assertEqual(len(concept['labels']), 2)
        for l in concept['labels']:
            self.assertIsInstance(l, dict)
            self.assertIn('label', l)
            self.assertIn('type', l)
            self.assertIn('language', l)
        self.assertIsInstance(concept['notes'], list)
        self.assertEqual(len(concept['notes']), 1)
        for n in concept['notes']:
            self.assertIsInstance(n, dict)
            self.assertIn('note', n)
            self.assertIn('type', n)
            self.assertIn('language', n)
        self.assertIsInstance(concept['broader'], list)
        self.assertIsInstance(concept['related'], list)
        self.assertIsInstance(concept['narrower'], list)

    def test_json_collection(self):
        from pyramid_skosprovider.utils import json_renderer
        c = Collection(
            id=species['id'],
            labels=species['labels'],
            members=species['members']
        )
        r = json_renderer({})
        jsonstring = r(c, {})
        coll = json.loads(jsonstring)
        self.assertIsInstance(coll, dict)
        self.assertEqual(coll['id'], 3)
        self.assertIsInstance(coll['label'], text_type)
        self.assertEqual(coll['type'], 'collection')
        self.assertIsInstance(coll['labels'], list)
        self.assertEqual(len(coll['labels']), 2)
        for l in coll['labels']:
            self.assertIsInstance(l, dict)
            self.assertIn('label', l)
            self.assertIn('type', l)
            self.assertIn('language', l)
