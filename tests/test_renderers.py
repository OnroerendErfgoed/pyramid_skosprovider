# -*- coding: utf8 -*-

from pyramid import testing

from .fixtures.data import (
    larch,
    chestnut,
    species,
    trees
)

from skosprovider.skos import (
    Concept,
    Collection,
    Label,
    Source
)

import json

import unittest
from unittest.mock import Mock


class TestRenderers(unittest.TestCase):

    def _assert_is_labels(self, labels):
        self.assertIsInstance(labels, list)
        for l in labels:
            self.assertIsInstance(l, Label)

    def test_concept_adapter(self):
        from pyramid_skosprovider.renderers import concept_adapter
        c = Concept(
            id=larch['id'],
            labels=larch['labels'],
            notes=larch['notes'],
            sources=larch['sources'],
            concept_scheme=trees.concept_scheme,
            matches=larch['matches']
        )
        request = testing.DummyRequest()
        m = Mock()
        request.skos_registry = m
        request.locale_name = 'nl'
        concept = concept_adapter(c, request)
        self.assertIsInstance(concept, dict)
        self.assertEqual(concept['id'], 1)
        self.assertIn('uri', concept)
        self.assertIsInstance(concept['label'], str)
        self.assertIn(concept['type'], 'concept')
        self.assertEqual(len(concept['labels']), 3)
        self._assert_is_labels(concept['labels'])
        assert 'matches' in concept
        assert 0 == len(concept['matches']['broad'])
        assert 0 == len(concept['matches']['narrow'])
        assert 0 == len(concept['matches']['related'])
        assert 0 == len(concept['matches']['exact'])
        assert 1 == len(concept['matches']['close'])
        assert 'subordinate_arrays' in concept
        assert 0 == len(concept['subordinate_arrays'])
        assert 'sources' in concept
        assert 1 == len(concept['sources'])
        assert 'label' in concept
        assert concept['label'] == 'De Lariks'

    def test_concept_adapter_en(self):
        from pyramid_skosprovider.renderers import concept_adapter
        c = Concept(
            id=larch['id'],
            labels=larch['labels'],
            concept_scheme=trees.concept_scheme,
        )
        request = testing.DummyRequest()
        m = Mock()
        request.skos_registry = m
        request.locale_name = 'en'
        concept = concept_adapter(c, request)
        assert 'label' in concept
        assert concept['label'] == 'The Larch'

    def test_collection_adapter(self):
        from pyramid_skosprovider.renderers import collection_adapter
        c = Collection(
            id=species['id'],
            labels=species['labels'],
            members=species['members'],
            concept_scheme=trees.concept_scheme
        )
        request = testing.DummyRequest()
        m = Mock()
        request.skos_registry = m
        request.locale_name = 'nl'
        collection = collection_adapter(c, request)
        self.assertIsInstance(collection, dict)
        self.assertEqual(collection['id'], 3)
        self.assertIsInstance(collection['label'], str)
        self.assertIn('label', collection)
        self.assertIn('uri', collection)
        self.assertEqual(collection['type'], 'collection')
        assert 4 == len(collection['labels'])
        self._assert_is_labels(collection['labels'])
        self.assertIn('notes', collection)
        assert collection['infer_concept_relations'] is True
        assert 'matches' not in collection
        assert 'superordinates' in collection
        assert 0 == len(collection['superordinates'])
        assert 0 == len(collection['sources'])
        assert collection['label'] == 'Bomen per soort'

    def test_source_adapter(self):
        from pyramid_skosprovider.renderers import source_adapter
        s = Source('<em>My citation</em>', 'HTML')
        source = source_adapter(s, Mock())
        assert isinstance(source, dict)
        assert 'citation' in source
        assert 'markup' in source
        assert source['markup'] == 'HTML'

    def test_json_concept(self):
        from pyramid_skosprovider.renderers import json_renderer
        c = Concept(
            id=larch['id'],
            uri=larch['uri'],
            labels=larch['labels'],
            notes=larch['notes'],
            concept_scheme=trees.concept_scheme,
            matches=larch['matches']
        )
        r = json_renderer({})
        request = testing.DummyRequest()
        m = Mock()
        request.skos_registry = m
        sys = {}
        sys['request'] = request
        jsonstring = r(c, sys)
        concept = json.loads(jsonstring)
        self.assertIsInstance(concept, dict)
        self.assertEqual(concept['id'], 1)
        self.assertEqual(concept['uri'], 'http://python.com/trees/larch')
        self.assertIsInstance(concept['label'], str)
        self.assertEqual(concept['type'], 'concept')
        self.assertIsInstance(concept['labels'], list)
        self.assertEqual(len(concept['labels']), 3)
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
            self.assertIn('markup', n)
        self.assertIsInstance(concept['broader'], list)
        self.assertIsInstance(concept['related'], list)
        self.assertIsInstance(concept['narrower'], list)
        assert 'matches' in concept
        for mt in ['broad', 'narrow', 'related', 'close', 'exact']:
            assert mt in concept['matches']
            assert list == type(concept['matches'][mt])
        assert 1 == len(concept['matches']['close'])

    def test_json_collection(self):
        from pyramid_skosprovider.renderers import json_renderer
        c = Collection(
            id=species['id'],
            uri=species['uri'],
            labels=species['labels'],
            notes=species['notes'],
            members=[larch['id']],
            concept_scheme=trees.concept_scheme
        )
        r = json_renderer({})
        m = Mock()
        config = {
            'get_provider.return_value.get_by_id.return_value': Concept(id=larch['id'], uri=larch['uri'], labels=larch['labels'])
        }
        m.configure_mock(**config)
        request = testing.DummyRequest()
        request.skos_registry = m
        sys = {}
        sys['request'] = request
        jsonstring = r(c, sys)
        coll = json.loads(jsonstring)
        assert isinstance(coll, dict)
        assert coll['id'] == 3
        assert coll['uri'] == 'http://python.com/trees/species'
        assert isinstance(coll['label'], str)
        assert coll['type'] == 'collection'
        assert isinstance(coll['labels'], list)
        assert 4 == len(coll['labels'])
        for l in coll['labels']:
            assert 'label' in l
            assert 'type' in l
            assert 'language' in l
        assert len(coll['notes']) == 1
        for n in coll['notes']:
            assert 'note' in n
            assert 'type' in n
            assert 'language' in n
            assert 'markup' in n
        assert len(coll['members']) == 1
        m = coll['members'][0]
        assert 'id' in m
        assert 'uri' in m
        assert 'type' in m
        assert 'label' in m
        assert 'matches' not in coll

    def test_map_relations_invalid_id(self):
        from pyramid_skosprovider.renderers import _map_relations
        p = Mock()
        config = {
            'get_by_id.return_value': False,
            'get_vocabulary_id.return_value': 'TESTPROVIDER'
        }
        p.configure_mock(**config)
        rels = _map_relations([5], p)
        assert len(rels) == 0
