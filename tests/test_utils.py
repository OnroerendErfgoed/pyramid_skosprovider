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
try:
    from unittest.mock import Mock
except ImportError:
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

    def test_import_concept_adapter(self):
        from pyramid_skosprovider.utils import concept_adapter as cau
        from pyramid_skosprovider.renderers import concept_adapter as car
        assert cau == car

    def test_import_collection_adapter(self):
        from pyramid_skosprovider.utils import collection_adapter as cau
        from pyramid_skosprovider.renderers import collection_adapter as car
        assert cau == car

    def test_import_source_adapter(self):
        from pyramid_skosprovider.utils import source_adapter as sau
        from pyramid_skosprovider.renderers import source_adapter as sar
        assert sau == sar

    def test_import_json_renderer(self):
        from pyramid_skosprovider.utils import json_renderer as jru
        from pyramid_skosprovider.renderers import json_renderer as jrr
        assert jru == jrr
