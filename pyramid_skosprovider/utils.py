# -*- coding: utf8 -*-
'''
This module contains a few utility functions.
'''

import re

import logging
log = logging.getLogger(__name__)


class QueryBuilder:

    def __init__(self, request, postprocess=False):
        self.request = request
        self.postprocess = postprocess
        self.no_result = False
        self.mode = self.request.params.get('mode', 'default')
        self.language = self.request.params.get(
            'language',
            self.request.locale_name
        )
        self.label = self.request.params.get('label', None)

    def _build_type(self, query):
        type = self.request.params.get('type', None)
        if type in ['concept', 'collection']:
            query['type'] = type
        return query

    def _build_label(self, query):
        if self.label not in [None, '*', '']:
            if self.mode == 'dijitFilteringSelect' and '*' in self.label:
                self.postprocess = True
                query['label'] = self.label.replace('*', '')
            else:
                query['label'] = self.label
        return query

    def _build_collection(self, query):
        coll = self.request.params.get('collection', None)
        if coll is not None:
            query['collection'] = {'id': coll, 'depth': 'all'}
        return query

    def _build_matches(self, query):
        match_uri = self.request.params.get('match', None)
        if match_uri is not None:
            query['matches'] = {'uri': match_uri}
            match_type = self.request.params.get('match_type', None)
            if match_type is not None:
                query['matches']['type'] = match_type
        return query

    def __call__(self):
        if self.mode == 'dijitFilteringSelect' and self.label == '':
            self.no_result = True
        q = {}
        q = self._build_type(q)
        q = self._build_label(q)
        q = self._build_collection(q)
        q = self._build_matches(q)
        return q


def parse_range_header(range):
    '''
    Parse a range header as used by the dojo Json Rest store.

    :param str range: The content of the range header to be parsed.
        eg. `items=0-9`
    :returns: A dict with keys start, finish and number or `False` if the
        range is invalid.
    '''
    match = re.match('^items=([0-9]+)-([0-9]+)$', range)
    if match:
        start = int(match.group(1))
        finish = int(match.group(2))
        if finish < start:
            finish = start
        return {
            'start': start,
            'finish': finish,
            'number': finish - start + 1
        }
    else:
        return False
