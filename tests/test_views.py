# -*- coding: utf8 -*-

import logging
from pyramid import testing

from pyramid.httpexceptions import (
    HTTPNotFound
)

import unittest
import pytest
from .fixtures.data import (
    trees
)

from skosprovider.skos import (
    Concept,
    ConceptScheme,
    Label
)

from skosprovider.registry import Registry

class StaticViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_skosprovider')
        self.regis = Registry()

    def tearDown(self):
        testing.tearDown()
        del self.config

    def _get_dummy_request(self, *args, **kwargs):
        request = testing.DummyRequest(*args, **kwargs)
        request.accept = 'application/json'
        request.skos_registry = self.regis
        return request

    def _get_static_view(self, request):
        from pyramid_skosprovider.views import StaticView
        return StaticView(request)

    def test_get_context(self):
        request = self._get_dummy_request()
        sv = self._get_static_view(request)
        ctxt = sv.get_context()
        assert isinstance(ctxt, dict)
        assert 'skos' in ctxt

class ProviderViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_skosprovider')
        self.regis = Registry()
        self.regis.register_provider(trees)

    def tearDown(self):
        testing.tearDown()
        del self.config
        del self.regis

    def _get_dummy_request(self, *args, **kwargs):
        request = testing.DummyRequest(*args, **kwargs)
        request.accept = 'application/json'
        request.skos_registry = self.regis
        return request

    def _get_provider_view(self, request):
        from pyramid_skosprovider.views import ProviderView
        return ProviderView(request)

    def test_get_unexisting_uri(self):
        request = self._get_dummy_request()
        request.matchdict = {'uri': 'urn:x-skosprovider:rain'}
        pv = self._get_provider_view(request)
        u = pv.get_uri()
        self.assertIsInstance(u, HTTPNotFound)

    def test_get_uri_sets_jsonld(self):
        request = self._get_dummy_request()
        request.accept = 'application/ld+json'
        request.matchdict = {'uri': 'http://python.com/trees'}
        pv = self._get_provider_view(request)
        u = pv.get_uri()
        assert request.response.content_type == 'application/ld+json'

    def test_get_uri_conceptscheme(self):
        request = self._get_dummy_request()
        request.matchdict = {'uri': 'http://python.com/trees'}
        pv = self._get_provider_view(request)
        u = pv.get_uri()
        assert '@context' in u
        assert 'uri' in u['@context']
        assert 'id' in u['@context']
        assert 'type' in u['@context']
        assert u['uri'] == 'http://python.com/trees'
        assert u['id'] == 'TREES'
        assert u['type'] == 'concept_scheme'

    def test_get_uri_concept(self):
        request = self._get_dummy_request()
        request.matchdict = {'uri': 'http://python.com/trees/larch'}
        pv = self._get_provider_view(request)
        u = pv.get_uri()

        assert '@context' in u
        assert 'uri' in u['@context']
        assert 'id' in u['@context']
        assert 'type' in u['@context']
        assert 'concept_scheme' in u['@context']
        assert 'concept' in u['@context']
        assert 'collection' in u['@context']
        assert u['uri'] == 'http://python.com/trees/larch'
        assert u['id'] == 1
        assert u['type'] == 'concept'
        assert u['concept_scheme'] == {
            'id': 'TREES',
            'type': 'skos:ConceptScheme',
            'uri': 'http://python.com/trees',
        }

    def test_get_uri_collection(self):
        request = self._get_dummy_request()
        request.matchdict = {'uri': 'http://python.com/trees/species'}
        pv = self._get_provider_view(request)
        u = pv.get_uri()

        assert '@context' in u
        assert 'uri' in u['@context']
        assert 'id' in u['@context']
        assert 'type' in u['@context']
        assert 'concept_scheme' in u['@context']
        assert 'concept' in u['@context']
        assert 'collection' in u['@context']
        assert u['uri'] == 'http://python.com/trees/species'
        assert u['id'] == 3
        assert u['type'] == 'collection'
        assert u['concept_scheme'] == {
            'id': 'TREES',
            'type': 'skos:ConceptScheme',
            'uri': 'http://python.com/trees',
        }

    def test_get_conceptschemes(self):
        request = self._get_dummy_request()
        pv = self._get_provider_view(request)
        conceptschemes = pv.get_conceptschemes()
        self.assertIsInstance(conceptschemes, list)
        for cs in conceptschemes:
            assert isinstance(cs, dict)
            assert 'id' in cs
            assert 'uri' in cs
            assert 'label' in cs

    def test_get_conceptschemes_jsonld(self):
        request = self._get_dummy_request()
        request.accept = 'application/ld+json'
        pv = self._get_provider_view(request)
        conceptschemes = pv.get_conceptschemes()
        self.assertIsInstance(conceptschemes, list)
        for cs in conceptschemes:
            assert isinstance(cs, dict)
            assert 'id' in cs
            assert 'uri' in cs
            assert 'label' in cs
            assert '@context' in cs


    def test_get_conceptscheme(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        cs = pv.get_conceptscheme()
        self.assertEqual(
            {
                'id': 'TREES',
                'uri': 'http://python.com/trees',
                'label': 'Different types of trees',
                'subject': [],
                'labels': [
                    Label('Different types of trees', 'prefLabel', 'en'),
                    Label('Verschillende soorten bomen', 'prefLabel', 'nl')
                ],
                'notes': [],
                'sources': [],
                'languages': []
            },
            cs
        )

    def test_get_conceptscheme_jsonld(self):
        request = self._get_dummy_request()
        request.accept = 'application/ld+json'
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        cs = pv.get_conceptscheme_jsonld()
        assert isinstance(cs, ConceptScheme)

    def test_get_unexisting_conceptscheme(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'PARROTS'}
        pv = self._get_provider_view(request)
        cs = pv.get_conceptscheme()
        self.assertIsInstance(cs, HTTPNotFound)

    def test_get_unexisting_conceptscheme_jsonld(self):
        request = self._get_dummy_request()
        request.accept = 'application/ld+json'
        request.matchdict = {'scheme_id': 'PARROTS'}
        pv = self._get_provider_view(request)
        cs = pv.get_conceptscheme_jsonld()
        self.assertIsInstance(cs, HTTPNotFound)

    def test_get_concepts(self):
        request = self._get_dummy_request()
        pv = self._get_provider_view(request)
        concepts = pv.get_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(3, len(concepts))
        for c in concepts:
            self.assertIsInstance(c, dict)
            self.assertIn('id', c)

    def test_get_concepts_language(self):
        request = self._get_dummy_request({
            'language': 'en'
        },
            locale_name='nl'
        )
        request.matchdict = {
            'scheme_id': 'TREES'
        }
        pv = self._get_provider_view(request)
        children = pv.get_concepts()
        request_locale = self._get_dummy_request(
            locale_name='nl'
        )
        request_locale.matchdict = {
            'scheme_id': 'TREES'
        }
        pv_locale = self._get_provider_view(request_locale)
        children_locale = pv_locale.get_concepts()
        self.assertEqual(children[0]['id'], children_locale[0]['id'])
        self.assertNotEqual(children[0]['label'], children_locale[0]['label'])

    def test_get_concepts_provider_subjects(self):
        request = self._get_dummy_request({
            'providers.subject': 'doesnt exist'
        })
        pv = self._get_provider_view(request)
        concepts = pv.get_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(0, len(concepts))

    def test_get_concepts_provider_ids(self):
        request = self._get_dummy_request({
            'providers.ids': 'PARROTS'
        })
        pv = self._get_provider_view(request)
        concepts = pv.get_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(0, len(concepts))

    def test_get_concepts_search_type_concept(self):
        request = self._get_dummy_request({
            'type': 'concept'
        })
        pv = self._get_provider_view(request)
        concepts = pv.get_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(2, len(concepts))

    def test_get_concepts_search_type_concept(self):
        request = self._get_dummy_request({
            'label': 'De lariks'
        })
        pv = self._get_provider_view(request)
        concepts = pv.get_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(1, len(concepts))

    def test_get_concepts_search_dfs_empty_label(self):
        request = self._get_dummy_request({
            'type': 'concept',
            'mode': 'dijitFilteringSelect',
            'label': ''
        })
        pv = self._get_provider_view(request)
        concepts = pv.get_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(0, len(concepts))

    def test_get_concepts_search_dfs_all(self):
        request = self._get_dummy_request({
            'type': 'concept',
            'mode': 'dijitFilteringSelect',
            'label': '*'
        })
        pv = self._get_provider_view(request)
        concepts = pv.get_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(2, len(concepts))

    def test_get_concepts_search_dfs_label_star_postfix(self):
        request = self._get_dummy_request({
            'mode': 'dijitFilteringSelect',
            'label': 'soo*',
            'language': 'nl-BE'
        })
        pv = self._get_provider_view(request)
        concepts = pv.get_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(0, len(concepts))

    def test_get_concepts_search_dfs_label_star_postfix_en(self):
        request = self._get_dummy_request({
            'mode': 'dijitFilteringSelect',
            'label': 'The*',
            'language': 'en'
        })
        pv = self._get_provider_view(request)
        concepts = pv.get_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(2, len(concepts))

    def test_get_concepts_search_dfs_label_star_prefix(self):
        request = self._get_dummy_request({
            'mode': 'dijitFilteringSelect',
            'label': '*kastanje',
            'language': 'nl-BE'
        })
        pv = self._get_provider_view(request)
        concepts = pv.get_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(1, len(concepts))

    def test_get_concepts_search_dfs_label_star_allfix(self):
        request = self._get_dummy_request({
            'mode': 'dijitFilteringSelect',
            'label': '*ch*',
            'language': 'en'
        })
        pv = self._get_provider_view(request)
        concepts = pv.get_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(2, len(concepts))

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
            'label': 'De *',
            'language': 'nl-BE'
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
            'label': '*iks',
            'language': 'nl-BE'
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
            'label': '*Larik*',
            'language': 'nl-BE'
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
        self.assertEqual(1, concept.id)

    def test_get_unexsisting_concept(self):
        request = self._get_dummy_request()
        request.matchdict = {
            'scheme_id': 'TREES',
            'c_id': 123456789
        }
        pv = self._get_provider_view(request)
        concept = pv.get_concept()
        self.assertIsInstance(concept, HTTPNotFound)

    def test_get_concept_unexisting_conceptscheme(self):
        request = self._get_dummy_request()
        request.matchdict = {
            'scheme_id': 'PARROTS',
            'c_id': 1
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
        request.params = {
            'language': 'nl-BE'
        }
        pv = self._get_provider_view(request)
        children = pv.get_concept_display_children()
        self.assertIsInstance(children, list)
        for c in children:
            self.assertIn('id', c)
            self.assertIn('uri', c)
            self.assertIn('label', c)
            self.assertIn('type', c)

    def test_get_concept_display_children_language(self):
        request = self._get_dummy_request({'language': 'nl-BE'})
        request.matchdict = {
            'scheme_id': 'TREES',
            'c_id': 3
        }
        pv = self._get_provider_view(request)
        children = pv.get_concept_display_children()
        request_locale= self._get_dummy_request()
        request_locale.locale_name = 'en'
        request_locale.matchdict = {
            'scheme_id': 'TREES',
            'c_id': 3
        }
        pv_locale = self._get_provider_view(request_locale)
        children_locale = pv_locale.get_concept_display_children()
        self.assertEqual(children[0]['id'], children_locale[0]['id'])
        self.assertNotEqual(children[0]['label'], children_locale[0]['label'])

    def test_get_unexsisting_concept_display_children(self):
        request = self._get_dummy_request()
        request.matchdict = {
            'scheme_id': 'TREES',
            'c_id': 123456789
        }
        pv = self._get_provider_view(request)
        concept = pv.get_concept_display_children()
        self.assertIsInstance(concept, HTTPNotFound)

    def test_get_concept_display_children_unexisting_conceptscheme(self):
        request = self._get_dummy_request()
        request.matchdict = {
            'scheme_id': 'PARROTS',
            'c_id': 1
        }
        pv = self._get_provider_view(request)
        concept = pv.get_concept_display_children()
        self.assertIsInstance(concept, HTTPNotFound)

    def test_get_concept_expand(self):
        request = self._get_dummy_request()
        request.matchdict = {
            'scheme_id': 'TREES',
            'c_id': 1
        }
        pv = self._get_provider_view(request)
        expanded = pv.get_expand()
        self.assertIsInstance(expanded, list)
        self.assertIn(1, expanded)

    def test_get_collection_expand(self):
        request = self._get_dummy_request()
        request.matchdict = {
            'scheme_id': 'TREES',
            'c_id': 3
        }
        pv = self._get_provider_view(request)
        expanded = pv.get_expand()
        self.assertIsInstance(expanded, list)
        self.assertIn(1, expanded)
        self.assertIn(2, expanded)
        self.assertNotIn(3, expanded)

    def test_get_expand_no_resource(self):
        request = self._get_dummy_request()
        request.matchdict = {
            'scheme_id': 'TREES',
            'c_id': 'no_resource'
        }
        pv = self._get_provider_view(request)
        expanded = pv.get_expand()
        self.assertIsInstance(expanded, HTTPNotFound)

    def test_get_expand_unexisting_conceptscheme(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'PARROTS'}
        pv = self._get_provider_view(request)
        tc = pv.get_conceptscheme_top_concepts()
        self.assertIsInstance(tc, HTTPNotFound)

    def test_get_top_concepts_unexisting_conceptscheme(self):
        request = self._get_dummy_request()
        request.matchdict = {
            'scheme_id': 'PARROTS',
            'c_id': 1
        }
        pv = self._get_provider_view(request)
        expanded = pv.get_expand()
        self.assertIsInstance(expanded, HTTPNotFound)

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

    def test_get_top_concepts_language(self):
        request = self._get_dummy_request({'language': 'nl-BE'})
        request.matchdict = {
            'scheme_id': 'TREES',
            'c_id': 1
        }
        pv = self._get_provider_view(request)
        children = pv.get_conceptscheme_top_concepts()
        request_locale= self._get_dummy_request()
        request_locale.locale_name = 'en'
        request_locale.matchdict = {
            'scheme_id': 'TREES',
            'c_id': 1
        }
        pv_locale = self._get_provider_view(request_locale)
        children_locale = pv_locale.get_conceptscheme_top_concepts()
        self.assertEqual(children[0]['id'], children_locale[0]['id'])
        self.assertNotEqual(children[0]['label'], children_locale[0]['label'])

    def test_get_display_top_unexisting_conceptscheme(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'PARROTS'}
        pv = self._get_provider_view(request)
        tc = pv.get_conceptscheme_display_top()
        self.assertIsInstance(tc, HTTPNotFound)

    def test_get_display_top(self):
        request = self._get_dummy_request()
        request.matchdict = {'scheme_id': 'TREES'}
        request.params = {
            'language': 'nl-BE'
        }
        pv = self._get_provider_view(request)
        tc = pv.get_conceptscheme_display_top()
        self.assertIsInstance(tc, list)
        for c in tc:
            self.assertIn('id', c)
            self.assertIn('uri', c)
            self.assertIn('label', c)
            self.assertIn('type', c)

    def test_get_display_top_language(self):
        request = self._get_dummy_request({'language': 'nl-BE'})
        request.matchdict = {
            'scheme_id': 'TREES',
            'c_id': 1
        }
        pv = self._get_provider_view(request)
        children = pv.get_conceptscheme_display_top()
        request_locale= self._get_dummy_request()
        request_locale.locale_name = 'en'
        request_locale.matchdict = {
            'scheme_id': 'TREES',
            'c_id': 1
        }
        pv_locale = self._get_provider_view(request_locale)
        children_locale = pv_locale.get_conceptscheme_display_top()
        self.assertEqual(children[0]['id'], children_locale[0]['id'])
        self.assertNotEqual(children[0]['label'], children_locale[0]['label'])

    def test_get_conceptscheme_concepts_search_sort_id_asc(self):
        request = self._get_dummy_request({
            'sort': '+id',
            'language': 'nl-BE'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(1, concepts[0]['id'])

    def test_get_conceptscheme_concepts_search_sort_id_space_is_asc(self):
        request = self._get_dummy_request({
            'sort': ' id',
            'language': 'nl-BE'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(1, concepts[0]['id'])

    def test_get_conceptscheme_concepts_search_sort_id_undefined_is_asc(self):
        request = self._get_dummy_request({
            'sort': 'id',
            'language': 'nl-BE'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(1, concepts[0]['id'])

    def test_get_conceptscheme_concepts_search_sort_id_desc(self):
        request = self._get_dummy_request({
            'sort': '-id',
            'language': 'nl-BE'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual(3, concepts[0]['id'])

    def test_get_conceptscheme_concepts_search_sort_label_default(self):
        request = self._get_dummy_request({
            'sort': 'label',
            'language': 'nl-BE'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual("Bomen per soort", concepts[0]['label'])

    def test_get_conceptscheme_concepts_search_sort_label_asc(self):
        request = self._get_dummy_request({
            'sort': '+label',
            'language': 'nl-BE'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual("Bomen per soort", concepts[0]['label'])

    def test_get_conceptscheme_concepts_search_sort_label_desc(self):
        request = self._get_dummy_request({
            'sort': '-label',
            'language': 'nl-BE'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual("De Paardekastanje", concepts[0]['label'])

    def test_get_conceptscheme_concepts_search_sort_sortlabel_asc(self):
        request = self._get_dummy_request({
            'sort': '+sortlabel',
            'language': 'nl-BE'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual("De Paardekastanje", concepts[0]['label'])

    def test_get_conceptscheme_concepts_search_sort_sortlabel_desc(self):
        request = self._get_dummy_request({
            'sort': '-sortlabel',
            'language': 'nl-BE'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)
        self.assertEqual("De Lariks", concepts[0]['label'])

    def test_get_conceptscheme_concepts_search_sort_unexisting_field(self):
        request = self._get_dummy_request({
            'sort': '-foo'
        })
        request.matchdict = {'scheme_id': 'TREES'}
        pv = self._get_provider_view(request)
        concepts = pv.get_conceptscheme_concepts()
        self.assertIsInstance(concepts, list)

    def test_get_concept_scheme_concepts_language(self):
        request = self._get_dummy_request({'language': 'nl-BE'})
        request.matchdict = {
            'scheme_id': 'TREES'
        }
        pv = self._get_provider_view(request)
        children = pv.get_conceptscheme_concepts()
        request_locale= self._get_dummy_request()
        request_locale.locale_name = 'en'
        request_locale.matchdict = {
            'scheme_id': 'TREES'
        }
        pv_locale = self._get_provider_view(request_locale)
        children_locale = pv_locale.get_conceptscheme_concepts()
        self.assertEqual(children[0]['id'], children_locale[0]['id'])
        self.assertNotEqual(children[0]['label'], children_locale[0]['label'])

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
