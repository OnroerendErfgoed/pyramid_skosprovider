# -*- coding: utf8 -*-

from __future__ import unicode_literals

from pyramid.config import Configurator

from pyramid.compat import (
    ascii_native_,
    string_types
)

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
        settings = {}
        app = skosmain({}, **settings)
        self.testapp = TestApp(app)

    def tearDown(self):
        del self.testapp


class RestFunctionalTests(FunctionalTests):

    def test_get_uri_cs_json(self):
        res = self.testapp.get(
            '/uris?uri=http://python.com/trees',
            {},
            {ascii_native_('Accept'): ascii_native_('application/json')}
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
            {ascii_native_('Accept'): ascii_native_('application/json')}
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
            {ascii_native_('Accept'): ascii_native_('application/json')}
        )
        res2 = self.testapp.get(
            '/uris/http://python.com/trees',
            {},
            {ascii_native_('Accept'): ascii_native_('application/json')}
        )
        self.assertEqual(res1.body, res2.body)

    def test_get_uri_no_uri(self):
        res = self.testapp.get(
            '/uris',
            {},
            {ascii_native_('Accept'): ascii_native_('application/json')},
            status=400
        )
        self.assertEqual('400 Bad Request', res.status)

    def test_get_conceptschemes_json(self):
        res = self.testapp.get(
            '/conceptschemes',
            {},
            {ascii_native_('Accept'): ascii_native_('application/json')})
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_get_conceptscheme_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES',
            {},
            {ascii_native_('Accept'): ascii_native_('application/json')})
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

    def test_get_conceptschemes_trees_cs_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c',
            {},
            {ascii_native_('Accept'): ascii_native_('application/json')}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsInstance(res.headers['Content-Range'], string_types)
        self.assertEqual('items 0-2/3', res.headers['Content-Range'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)

    def test_get_conceptschemes_trees_cs_slice_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c',
            {},
            {
                ascii_native_('Accept'): ascii_native_('application/json'),
                ascii_native_('Range'): ascii_native_('items=2-2')
            }
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        self.assertIsInstance(res.headers['Content-Range'], string_types)
        self.assertEqual('items 2-2/3', res.headers['Content-Range'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_get_conceptschemes_trees_larch_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c/1',
            {},
            {ascii_native_('Accept'): ascii_native_('application/json')}
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

    def test_get_conceptschemes_trees_species_json(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c/3',
            {},
            {ascii_native_('Accept'): ascii_native_('application/json')}
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

    def test_get_conceptscheme_concepts_search_dfs_label_star(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c?language=nl-BE',
            {
                'type': 'concept',
                'mode': 'dijitFilteringSelect',
                'label': 'De *'
            },
            {ascii_native_('Accept'): ascii_native_('application/json')}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertEqual(2, len(data))

    def test_get_conceptscheme_concepts_search_dfs_all(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/c',
            {'mode': 'dijitFilteringSelect', 'label': '*'},
            {ascii_native_('Accept'): ascii_native_('application/json')}
        )
        self.assertEqual('200 OK', res.status)
        self.assertIn('application/json', res.headers['Content-Type'])
        data = json.loads(res.body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertEqual(3, len(data))

    def test_get_top_concepts(self):
        res = self.testapp.get(
            '/conceptschemes/TREES/topconcepts',
            {ascii_native_('Accept'): ascii_native_('application/json')}
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
