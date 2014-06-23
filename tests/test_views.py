# -*- coding: utf8 -*-

from __future__ import unicode_literals

from pyramid import testing

from pyramid.httpexceptions import (
    HTTPNotFound
)

from .fixtures.data import (
    trees
)

from skosprovider.skos import (
    Concept
)

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa


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

    def test_get_conceptscheme_concepts_range_one_item(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'TREES'}
        request.headers['Range'] = 'items=0-0'
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertEqual(1, len(concepts))

    def test_get_conceptscheme_concepts_range_final_items(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'TREES'}
        request.headers['Range'] = 'items=1-2'
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertEqual(2, len(concepts))

    def test_get_conceptscheme_concepts_invalid_range(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'TREES'}
        request.headers['Range'] = 'items=a-2'
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertEqual(3, len(concepts))

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

    def test_get_concept_display_children(self):
        request = self._get_dummy_request()
        request.matchdict = {
            'scheme_id': 'TREES',
            'c_id': 1
        }
        pv = self._get_provider_view(request)
        children = pv.get_concept_display_children()
        self.assertIsInstance(children, list)
        for c in children:
            self.assertIn('id', c)
            self.assertIn('uri', c)
            self.assertIn('label', c)
            self.assertIn('type', c)

    def test_get_unexsisting_concept_display_children(self):
        request = self._get_dummy_request()
        request.matchdict = {
            'scheme_id': 'TREES',
            'c_id': 123456789
        }
        pv = self._get_provider_view(request)
        concept = pv.get_concept_display_children()
        self.assertIsInstance(concept, HTTPNotFound)

    def test_get_top_concepts_unexisting_conceptscheme(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'PARROTS'}
        pv = self._get_provider_view(request)
        tc = pv.get_conceptscheme_top_concepts()
        self.assertIsInstance(tc, HTTPNotFound)

    def test_get_top_concepts(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        tc = pv.get_conceptscheme_top_concepts()
        self.assertIsInstance(tc, list)
        self.assertEqual(2, len(tc))
        first = tc[0]
        for c in tc:
            self.assertIn('id', c)
            self.assertIn('uri', c)
            self.assertIn('label', c)
            self.assertEqual('concept', c['type'])

    def test_get_display_top_unexisting_conceptscheme(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'PARROTS'}
        pv = self._get_provider_view(request)
        tc = pv.get_conceptscheme_display_top()
        self.assertIsInstance(tc, HTTPNotFound)

    def test_get_display_top(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        tc = pv.get_conceptscheme_display_top()
        self.assertIsInstance(tc, list)
        for c in tc:
            self.assertIn('id', c)
            self.assertIn('uri', c)
            self.assertIn('label', c)
            self.assertIn('type', c)

    def test_get_conceptscheme_concepts_search_sort_id_asc(self):
        request = self._get_dummy_request({
            'sort': '+id'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(1, concepts[0]['id'])

    def test_get_conceptscheme_concepts_search_sort_id_space_is_asc(self):
        request = self._get_dummy_request({
            'sort': ' id'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(1, concepts[0]['id'])

    def test_get_conceptscheme_concepts_search_sort_id_undefined_is_asc(self):
        request = self._get_dummy_request({
            'sort': 'id'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(1, concepts[0]['id'])

    def test_get_conceptscheme_concepts_search_sort_id_desc(self):
        request = self._get_dummy_request({
            'sort': '-id'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(3, concepts[0]['id'])

    def test_get_conceptscheme_concepts_search_sort_label_default(self):
        request = self._get_dummy_request({
            'sort': 'label'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual("Bomen per soort", concepts[0]['label'])

    def test_get_conceptscheme_concepts_search_sort_label_asc(self):
        request = self._get_dummy_request({
            'sort': '+label'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual("Bomen per soort", concepts[0]['label'])

    def test_get_conceptscheme_concepts_search_sort_label_desc(self):
        request = self._get_dummy_request({
            'sort': '-label'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual("De Paardekastanje", concepts[0]['label'])

    def test_get_conceptscheme_concepts_search_sort_unexisting_field(self):
        request = self._get_dummy_request({
            'sort': '-foo'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)

    def test_get_conceptscheme_concepts_search_sort_empty_result(self):
        request = self._get_dummy_request({
            'sort': '-foo',
            'label': 'bar'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(0, len(concepts))
