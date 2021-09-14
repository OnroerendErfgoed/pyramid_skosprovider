# -*- coding: utf8 -*-

from pyramid.config import Configurator

import json

from webtest import TestApp

import unittest

from .fixtures.data import (
    trees
)


def skosmain(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """

    # Set up pyramid
    config = Configurator(settings=settings)

    config.include('pyramid_skosprovider')

    skosregis = config.get_skos_registry()
    skosregis.register_provider(trees)

    return config.make_wsgi_app()


class FunctionalTests(unittest.TestCase):

    def setUp(self):
        settings = {
            'skosprovider.skosregistry_location': 'registry'
        }
        app = skosmain({}, **settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        del self.testapp


class RestFunctionalTests(FunctionalTests):

    def test_get_context_json(self):
        res = self.testapp.get(
            '/jsonld/context/skos',
            {},
            {'Accept': 'application/json'}
        )
        assert res.status == '200 OK'
        assert 'application/json' in res.headers['Content-Type']
        data = json.loads(res.body.decode('utf-8'))
        assert isinstance(data, dict)
        assert 'skos' in data
        assert 'dct' in data

    def test_get_context_jsonld(self):
        res = self.testapp.get(
            '/jsonld/context/skos',
            {},
            {'Accept': 'application/ld+json'}
        )
        assert res.status == '200 OK'
        assert 'application/ld+json' in res.headers['Content-Type']
        data = json.loads(res.body.decode('utf-8'))
        assert isinstance(data, dict)
        assert 'skos' in data
        assert 'dct' in data

    def test_get_uri_cs_json(self):
        res = self.testapp.get(
            '/uris?uri=http://python.com/trees',
            {},
            {'Accept': 'application/json'}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, dict)
        self.assertIn('uri', data)
        self.assertIn('id', data)
        self.assertIn('type', data)

    def test_get_uri_c_json(self):
        res = self.testapp.get(
            '/uris?uri=http%3A%2F%2Fpython.com%2Ftrees%2Flarch',
            {},
            {'Accept': 'application/json'}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, dict)
        self.assertIn('uri', data)
        self.assertIn('id', data)
        self.assertIn('type', data)
        self.assertIn('concept_scheme', data)

    def test_get_uri_deprecated_way(self):
        res1 = self.testapp.get(
            '/uris?uri=http://python.com/trees',
            {},
            {'Accept': 'application/json'}
        )
        res2 = self.testapp.get(
            '/uris/http://python.com/trees',
            {},
            {'Accept': 'application/json'}
        )
        self.assertEqual(res1.body, res2.body)

    def test_get_uri_no_uri(self):
        res = self.testapp.get(
            '/uris',
            {},
            {'Accept': 'application/json'},
            status=400
        )
        self.assertEqual('400 Bad Request', res.status)

    def test_get_conceptschemes_json(self):
        res = self.testapp.get(
            '/conceptschemes',
            {},
            {'Accept': 'application/json'}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_get_conceptscheme_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES',
            {},
            {'Accept': 'application/json'}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, dict)
        self.assertIn('id', data)
        self.assertIn('uri', data)
        self.assertIn('subject', data)
        self.assertIn('label', data)
        self.assertIn('labels', data)
        self.assertIn('sources', data)
        self.assertEqual(len(data['labels']), 2)
        for l in data['labels']:
            self.assertIsInstance(l, dict)
        self.assertIn('notes', data)

    def test_get_conceptscheme_jsonld(self):
        res = self.testapp.get(
            '/conceptschemes/TREES',
            {},
            {'Accept': 'application/ld+json'}
        )
        assert res.status == '200 OK'
        assert 'application/ld+json' in res.headers['Content-Type']
        data = json.loads(res.body.decode('utf-8'))
        assert isinstance(data, dict)
        assert 'id' in data
        assert 'uri'in data
        assert 'label' in data
        assert 'labels' in data
        assert 'sources' in data
        assert 'notes' in data
        assert 'type' in data
        assert '@context' in data
        assert '/jsonld/context/skos' in data['@context']

    def test_get_conceptscheme_jsonld_url(self):
        res = self.testapp.get(
            '/conceptschemes/TREES.jsonld'
        )
        assert res.status == '200 OK'
        assert 'application/ld+json' in res.headers['Content-Type']
        data = json.loads(res.body.decode('utf-8'))
        res2 = self.testapp.get(
            '/conceptschemes/TREES',
            {},
            {'Accept': 'application/ld+json'}
        )
        data2 = json.loads(res2.body.decode('utf-8'))
        assert data == data2

    def test_get_conceptschemes_trees_cs_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c',
            {},
            {'Accept': 'application/json'}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsInstance(res.headers['Content-Range'], str)
        self.assertEqual('items 0-2/3', res.headers['Content-Range'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)

    def test_get_conceptschemes_trees_cs_slice_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c',
            {},
            {
                'Accept': 'application/json',
                'Range': 'items=2-2'
            }
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsInstance(res.headers['Content-Range'], str)
        self.assertEqual('items 2-2/3', res.headers['Content-Range'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_get_conceptschemes_trees_larch_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c/1',
            {},
            {'Accept': 'application/json'}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, dict)
        self.assertIn('id', data)
        self.assertIn('label', data)
        self.assertIn('labels', data)
        self.assertIn('notes', data)
        self.assertIn('sources', data)
        self.assertEqual('concept', data['type'])
        self.assertIn('narrower', data)
        self.assertIn('broader', data)
        self.assertIn('related', data)
        self.assertNotIn('members', data)
        self.assertIn('member_of', data)

    def test_get_conceptschemes_trees_larch_jsonld(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c/1',
            {},
            {'Accept': 'application/ld+json'}
        )
        assert res.status == '200 OK'
        assert 'application/ld+json' in res.headers['Content-Type']
        data = json.loads(res.body.decode('utf-8'))
        assert isinstance(data, dict)
        assert 'id' in data
        assert 'label' in data
        assert 'uri' in data
        assert 'type' in data
        assert '@context' in data
        assert '/jsonld/context/skos' in data['@context']

    def test_get_conceptschemes_trees_species_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c/3',
            {},
            {'Accept': 'application/json'}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, dict)
        self.assertIn('id', data)
        self.assertIn('label', data)
        self.assertIn('labels', data)
        self.assertIn('notes', data)
        self.assertEqual('collection', data['type'])
        self.assertNotIn('narrower', data)
        self.assertNotIn('broader', data)
        self.assertNotIn('related', data)
        self.assertIn('members', data)
        self.assertIn('member_of', data)

    def test_get_conceptschemes_trees_species_jsonld(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c/3',
            {},
            {'Accept': 'application/ld+json'}
        )
        assert res.status == '200 OK'
        assert 'application/ld+json' in res.headers['Content-Type']
        data = json.loads(res.body.decode('utf-8'))
        assert isinstance(data, dict)
        assert 'id' in data
        assert 'label' in data
        assert 'uri' in data
        assert 'type' in data
        assert '@context' in data
        assert '/jsonld/context/skos' in data['@context']

    def test_get_conceptschemes_trees_species_jsonld_url(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c/3.jsonld'
        )
        assert res.status == '200 OK'
        assert 'application/ld+json' in res.headers['Content-Type']
        data = json.loads(res.body.decode('utf-8'))
        res2 = self.testapp.get(
            '/conceptschemes/TREES/c/3',
            {},
            {'Accept': 'application/ld+json'}
        )
        data2 = json.loads(res2.body.decode('utf-8'))
        assert data == data2

    def test_get_conceptscheme_concepts_search_dfs_label_star_postfix(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c?language=nl-BE',
            {
                'mode': 'dijitFilteringSelect',
                'label': 'de *'
            },
            {'Accept': 'application/json'}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertEqual(2, len(data))

    def test_get_conceptscheme_concepts_search_dfs_label_star_prefix(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c?language=en',
            {
                'mode': 'dijitFilteringSelect',
                'label': '*nut'
            },
            {'Accept': 'application/json'}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertEqual(1, len(data))

    def test_get_conceptscheme_concepts_search_dfs_label_star_prepostfix(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c?language=nl-BE',
            {
                'mode': 'dijitFilteringSelect',
                'label': '*Lariks*'
            },
            {'Accept': 'application/json'}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertEqual(1, len(data))

    def test_get_conceptscheme_concepts_search_dfs_all(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c',
            {'mode': 'dijitFilteringSelect', 'label': '*'},
            {'Accept': 'application/json'}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertEqual(3, len(data))

    def test_get_top_concepts(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/topconcepts',
            {'Accept': 'application/json'}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertEqual(2, len(data))
        for c in data:
            self.assertIn('id', c)
            self.assertIn('uri', c)
            self.assertIn('label', c)
            self.assertEqual('concept', c['type'])
