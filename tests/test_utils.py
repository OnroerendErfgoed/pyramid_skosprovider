# -*- coding: utf8 -*-

from __future__ import unicode_literals

from pyramid.compat import (
    text_type
)

from .fixtures.data import (
    larch,
    species,
    trees
)

from skosprovider.skos import (
    Concept,
    Collection,
    Label
)

import json

import unittest


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
            notes=larch['notes'],
            concept_scheme=trees.concept_scheme,
            matches=larch['matches']
        )
        concept = concept_adapter(c, {})
        self.assertIsInstance(concept, dict)
        self.assertEqual(concept['id'], 1)
        self.assertIn('uri', concept)
        self.assertIsInstance(concept['label'], text_type)
        self.assertIn(concept['type'], 'concept')
        self.assertEqual(len(concept['labels']), 2)
        self._assert_is_labels(concept['labels'])
        assert 'matches' in concept
        assert 0 == len(concept['matches']['broad'])
        assert 0 == len(concept['matches']['narrow'])
        assert 0 == len(concept['matches']['related'])
        assert 0 == len(concept['matches']['exact'])
        assert 1 == len(concept['matches']['close'])
        assert 'subordinate_arrays' in concept
        assert 0 == len(concept['subordinate_arrays'])

    def test_collection_adapter(self):
        from pyramid_skosprovider.utils import collection_adapter
        c = Collection(
            id=species['id'],
            labels=species['labels'],
            members=species['members'],
            concept_scheme=trees.concept_scheme
        )
        collection = collection_adapter(c, {})
        self.assertIsInstance(collection, dict)
        self.assertEqual(collection['id'], 3)
        self.assertIsInstance(collection['label'], text_type)
        self.assertIn('label', collection)
        self.assertIn('uri', collection)
        self.assertEqual(collection['type'], 'collection')
        self.assertEqual(len(collection['labels']), 2)
        self._assert_is_labels(collection['labels'])
        self.assertIn('notes', collection)
        assert not 'matches' in collection
        assert 'superordinates' in collection
        assert 0 == len(collection['superordinates'])

    def test_json_concept(self):
        from pyramid_skosprovider.utils import json_renderer
        c = Concept(
            id=larch['id'],
            uri=larch['uri'],
            labels=larch['labels'],
            notes=larch['notes'],
            concept_scheme=trees.concept_scheme,
            matches=larch['matches']
        )
        r = json_renderer({})
        jsonstring = r(c, {})
        concept = json.loads(jsonstring)
        self.assertIsInstance(concept, dict)
        self.assertEqual(concept['id'], 1)
        self.assertEqual(concept['uri'], 'http://python.com/trees/larch')
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
        assert 'matches' in concept
        for mt in ['broad', 'narrow', 'related', 'close', 'exact']:
            assert mt in concept['matches']
            assert list == type(concept['matches'][mt])
        assert 1 == len(concept['matches']['close'])

    def test_json_collection(self):
        from pyramid_skosprovider.utils import json_renderer
        c = Collection(
            id=species['id'],
            uri=species['uri'],
            labels=species['labels'],
            notes=species['notes'],
            members=species['members'],
            concept_scheme=trees.concept_scheme
        )
        r = json_renderer({})
        jsonstring = r(c, {})
        coll = json.loads(jsonstring)
        self.assertIsInstance(coll, dict)
        self.assertEqual(coll['id'], 3)
        self.assertEqual(coll['uri'], 'http://python.com/trees/species')
        self.assertIsInstance(coll['label'], text_type)
        self.assertEqual(coll['type'], 'collection')
        self.assertIsInstance(coll['labels'], list)
        self.assertEqual(len(coll['labels']), 2)
        for l in coll['labels']:
            self.assertIsInstance(l, dict)
            self.assertIn('label', l)
            self.assertIn('type', l)
            self.assertIn('language', l)
        self.assertEqual(len(coll['notes']), 1)
        for n in coll['notes']:
            self.assertIsInstance(n, dict)
            self.assertIn('note', n)
            self.assertIn('type', n)
            self.assertIn('language', n)
        assert 'matches' not in coll
