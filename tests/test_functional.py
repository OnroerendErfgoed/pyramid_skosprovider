# -*- coding: utf8 -*-

from pyramid.config import Configurator

from webtest import TestApp

import unittest
import responses

from .fixtures.data import (
    trees
)

from pyld import jsonld


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

def register_ctxt_callback(responses, testapp):

    def callback(request):
        response = testapp.get(request.path_url, headers=request.headers)
        return 200, response.headers, response.text

    responses.add_callback(
        method = responses.GET,
        url = "http://localhost/jsonld/context/skos",
        callback = callback
    )
    return responses

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
            {'Accept': 'application/json'},
            status=200
        )
        assert 'application/json' in res.headers['Content-Type']
        data = res.json
        assert isinstance(data, dict)
        assert '@context' in data
        assert 'skos' in data['@context']
        assert 'dct' in data['@context']

    def test_get_context_jsonld(self):
        res = self.testapp.get(
            '/jsonld/context/skos',
            {},
            {'Accept': 'application/ld+json'},
            status=200
        )
        assert 'application/ld+json' in res.headers['Content-Type']
        data = res.json
        assert isinstance(data, dict)
        assert '@context' in data
        assert 'skos' in data['@context']
        assert 'dct' in data['@context']

    def test_get_uri_cs_json(self):
        res = self.testapp.get(
            '/uris?uri=http://python.com/trees',
            {},
            {'Accept': 'application/json'},
            status=200
        )
        self.assertIn('application/json', res.headers['Content-Type'])
        data = res.json
        self.assertIsInstance(data, dict)
        self.assertIn('uri', data)
        self.assertIn('id', data)
        self.assertIn('type', data)

    def test_get_uri_c_json(self):
        res = self.testapp.get(
            '/uris?uri=http%3A%2F%2Fpython.com%2Ftrees%2Flarch',
            {},
            {'Accept': 'application/json'},
            status=200
        )
        self.assertIn('application/json', res.headers['Content-Type'])
        data = res.json
        self.assertIsInstance(data, dict)
        self.assertIn('uri', data)
        self.assertIn('id', data)
        self.assertIn('type', data)
        self.assertIn('concept_scheme', data)

    def test_get_uri_deprecated_way(self):
        res1 = self.testapp.get(
            '/uris?uri=http://python.com/trees',
            {},
            {'Accept': 'application/json'},
            status=200
        )
        res2 = self.testapp.get(
            '/uris/http://python.com/trees',
            {},
            {'Accept': 'application/json'},
            status=200
        )
        self.assertEqual(res1.body, res2.body)

    def test_get_uri_no_uri(self):
        res = self.testapp.get(
            '/uris',
            {},
            {'Accept': 'application/json'},
            status=400
        )

    def test_get_conceptschemes_json(self):
        res = self.testapp.get(
            '/conceptschemes',
            {},
            {'Accept': 'application/json'},
            status=200
        )
        self.assertIn('application/json', res.headers['Content-Type'])
        data = res.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_get_conceptscheme_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES',
            {},
            {'Accept': 'application/json'},
            status=200
        )
        self.assertIn('application/json', res.headers['Content-Type'])
        data = res.json
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
            {'Accept': 'application/ld+json'},
            status=200
        )
        assert 'application/ld+json' in res.headers['Content-Type']
        data = res.json
        assert isinstance(data, dict)
        assert 'id' in data
        assert 'uri' in data
        assert 'label' in data
        assert 'labels' in data
        assert 'sources' in data
        assert '@context' in data
        assert '/jsonld/context/skos' in data['@context']

    def test_get_conceptscheme_jsonld_expand(self):
        
        res = self.testapp.get(
            '/conceptschemes/TREES',
            {},
            {'Accept': 'application/ld+json'},
            status=200
        )
        assert 'application/ld+json' in res.headers['Content-Type']
        data = res.json

        with responses.RequestsMock() as rsps:

            register_ctxt_callback(rsps, self.testapp)

            expanded = jsonld.expand(data)
            assert 'http://purl.org/dc/terms/identifier' in expanded[0]
            assert 'http://python.com/trees' == expanded[0]['@id']
            assert 'http://www.w3.org/2004/02/skos/core#ConceptScheme' in expanded[0]['@type']
            assert {'@value': 'TREES'} in expanded[0]['http://purl.org/dc/terms/identifier']
            assert 'http://www.w3.org/2004/02/skos/core#prefLabel' in expanded[0]

    def test_get_conceptscheme_jsonld_url(self):
        res = self.testapp.get(
            '/conceptschemes/TREES.jsonld',
            status=200
        )
        assert 'application/ld+json' in res.headers['Content-Type']
        data = res.json
        res2 = self.testapp.get(
            '/conceptschemes/TREES',
            {},
            {'Accept': 'application/ld+json'},
            status=200
        )
        data2 = res2.json
        assert data == data2

    def test_get_conceptschemes_trees_cs_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c',
            {},
            {'Accept': 'application/json'},
            status=200
        )
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsInstance(res.headers['Content-Range'], str)
        self.assertEqual('items 0-2/3', res.headers['Content-Range'])
        data = res.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)

    def test_get_conceptschemes_trees_cs_slice_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c',
            {},
            {
                'Accept': 'application/json',
                'Range': 'items=2-2'
            },
            status=200
        )
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsInstance(res.headers['Content-Range'], str)
        self.assertEqual('items 2-2/3', res.headers['Content-Range'])
        data = res.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_get_conceptschemes_trees_larch_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c/1',
            {},
            {'Accept': 'application/json'},
            status=200
        )
        self.assertIn('application/json', res.headers['Content-Type'])
        data = res.json
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
            {'Accept': 'application/ld+json'},
            status=200
        )
        assert 'application/ld+json' in res.headers['Content-Type']
        data = res.json
        assert isinstance(data, dict)
        assert 'id' in data
        assert 'label' in data
        assert 'uri' in data
        assert 'type' in data
        assert '@context' in data
        assert '/jsonld/context/skos' in data['@context']


    def test_get_conceptscheme_trees_larch_jsonld_expand(self):
        
        res = self.testapp.get(
            '/conceptschemes/TREES/c/1',
            {},
            {'Accept': 'application/ld+json'},
            status=200
        )
        assert 'application/ld+json' in res.headers['Content-Type']
        data = res.json

        with responses.RequestsMock() as rsps:

            register_ctxt_callback(rsps, self.testapp)

            expanded = jsonld.expand(data)
            assert 'http://purl.org/dc/terms/identifier' in expanded[0]
            assert 'http://python.com/trees/larch' == expanded[0]['@id']
            assert 'http://www.w3.org/2004/02/skos/core#Concept' in expanded[0]['@type']
            assert {'@value': 1} in expanded[0]['http://purl.org/dc/terms/identifier']
            assert 'http://www.w3.org/2004/02/skos/core#prefLabel' in expanded[0]

    def test_get_conceptschemes_trees_species_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c/3',
            {},
            {'Accept': 'application/json'},
            status=200
        )
        self.assertIn('application/json', res.headers['Content-Type'])
        data = res.json
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
            {'Accept': 'application/ld+json'},
            status=200
        )
        assert 'application/ld+json' in res.headers['Content-Type']
        data = res.json
        assert isinstance(data, dict)
        assert 'id' in data
        assert 'label' in data
        assert 'uri' in data
        assert 'type' in data
        assert '@context' in data
        assert '/jsonld/context/skos' in data['@context']

    def test_get_conceptscheme_trees_species_jsonld_expand(self):
        
        res = self.testapp.get(
            '/conceptschemes/TREES/c/3',
            {},
            {'Accept': 'application/ld+json'},
            status=200
        )
        assert 'application/ld+json' in res.headers['Content-Type']
        data = res.json

        with responses.RequestsMock() as rsps:

            register_ctxt_callback(rsps, self.testapp)

            expanded = jsonld.expand(data)
            assert 'http://purl.org/dc/terms/identifier' in expanded[0]
            assert 'http://python.com/trees/species' == expanded[0]['@id']
            assert 'http://www.w3.org/2004/02/skos/core#Collection' in expanded[0]['@type']
            assert {'@value': 3} in expanded[0]['http://purl.org/dc/terms/identifier']
            assert 'http://www.w3.org/2004/02/skos/core#prefLabel' in expanded[0]

    def test_get_conceptschemes_trees_species_jsonld_url(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c/3.jsonld',
            status=200
        )
        assert 'application/ld+json' in res.headers['Content-Type']
        data = res.json
        res2 = self.testapp.get(
            '/conceptschemes/TREES/c/3',
            {},
            {'Accept': 'application/ld+json'},
            status=200
        )
        data2 = res.json
        assert data == data2

    def test_get_conceptscheme_concepts_search_dfs_label_star_postfix(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c?language=nl-BE',
            {
                'mode': 'dijitFilteringSelect',
                'label': 'de *'
            },
            {'Accept': 'application/json'},
            status=200
        )
        self.assertIn('application/json', res.headers['Content-Type'])
        data = res.json
        self.assertIsInstance(data, list)
        self.assertEqual(2, len(data))

    def test_get_conceptscheme_concepts_search_dfs_label_star_prefix(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c?language=en',
            {
                'mode': 'dijitFilteringSelect',
                'label': '*nut'
            },
            {'Accept': 'application/json'},
            status=200
        )
        self.assertIn('application/json', res.headers['Content-Type'])
        data = res.json
        self.assertIsInstance(data, list)
        self.assertEqual(1, len(data))

    def test_get_conceptscheme_concepts_search_dfs_label_star_prepostfix(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c?language=nl-BE',
            {
                'mode': 'dijitFilteringSelect',
                'label': '*Lariks*'
            },
            {'Accept': 'application/json'},
            status=200
        )
        self.assertIn('application/json', res.headers['Content-Type'])
        data = res.json
        self.assertIsInstance(data, list)
        self.assertEqual(1, len(data))

    def test_get_conceptscheme_concepts_search_dfs_all(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c',
            {'mode': 'dijitFilteringSelect', 'label': '*'},
            {'Accept': 'application/json'},
            status=200
        )
        self.assertIn('application/json', res.headers['Content-Type'])
        data = res.json
        self.assertIsInstance(data, list)
        self.assertEqual(3, len(data))

    def test_get_top_concepts(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/topconcepts',
            {'Accept': 'application/json'},
            status=200
        )
        self.assertIn('application/json', res.headers['Content-Type'])
        data = res.json
        self.assertIsInstance(data, list)
        self.assertEqual(2, len(data))
        for c in data:
            self.assertIn('id', c)
            self.assertIn('uri', c)
            self.assertIn('label', c)
            self.assertEqual('concept', c['type'])
