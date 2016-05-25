# -*- coding: utf8 -*-

from __future__ import unicode_literals

from pyramid import testing

from pyramid.compat import (
    text_type
)

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
from mock import Mock

class TestQueryBuilder:

    def _get_dummy_request(self, *args, **kwargs):
        request = testing.DummyRequest(*args, **kwargs)
        return request

    def _get_fut(self, request=None, postprocess=False):
        from pyramid_skosprovider.utils import QueryBuilder
        if not request:
            request = self._get_dummy_request()
        qb = QueryBuilder(request, postprocess)
        return qb

    def test_simple(self):
        qb = self._get_fut()
        assert qb.postprocess is False
        q = qb()
        assert isinstance(q, dict)

    def test_build_type(self):
        request = self._get_dummy_request({'type': 'concept'})
        qb = self._get_fut(request)
        q = qb()
        assert isinstance(q, dict)
        assert 'type' in q
        assert q['type'] == 'concept'

    def test_build_invalid_type(self):
        request = self._get_dummy_request({'type': 'conceptscheme'})
        qb = self._get_fut(request)
        q = qb()
        assert isinstance(q, dict)
        assert 'type' not in q

    def test_build_label_dfs_with_star(self):
        request = self._get_dummy_request({
            'mode': 'dijitFilteringSelect',
            'label': 'Di*'
        })
        qb = self._get_fut(request)
        q = qb()
        assert isinstance(q, dict)
        assert 'label' in q
        assert q['label'] == 'Di'

    def test_build_collection(self):
        request = self._get_dummy_request({
            'collection': 3
        })
        qb = self._get_fut(request)
        q = qb()
        assert isinstance(q, dict)
        assert 'collection' in q
        assert q['collection'] == {'id': 3, 'depth': 'all'}

class TestRangeHeaders(unittest.TestCase):

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


class TestRenderers(unittest.TestCase):
    '''
    Renderers have been moved from pyramid_skosprovider.utils to pyramid_skosprovider.renderers.
    Maintain tests until 0.8.0 when they will be removed.
    '''

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
            sources=larch['sources'],
            concept_scheme=trees.concept_scheme,
            matches=larch['matches']
        )
        concept = concept_adapter(c, Mock())
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
        assert 'sources' in concept
        assert 1 == len(concept['sources'])

    def test_collection_adapter(self):
        from pyramid_skosprovider.utils import collection_adapter
        c = Collection(
            id=species['id'],
            labels=species['labels'],
            members=species['members'],
            concept_scheme=trees.concept_scheme
        )
        collection = collection_adapter(c, Mock())
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
        assert 0 == len(collection['sources'])

    def test_source_adapter(self):
        from pyramid_skosprovider.utils import source_adapter
        s = Source('<em>My citation</em>', 'HTML')
        source = source_adapter(s, Mock())
        assert isinstance(source, dict)
        assert 'citation' in source
        assert 'markup' in source
        assert source['markup'] == 'HTML'

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
        jsonstring = r(c, Mock())
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
        from pyramid_skosprovider.utils import json_renderer
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
        assert isinstance(coll['label'], text_type)
        assert coll['type'] == 'collection'
        assert isinstance(coll['labels'], list)
        assert len(coll['labels']) == 2
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
