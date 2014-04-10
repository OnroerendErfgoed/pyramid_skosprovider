# -*- coding: utf8 -*-

from __future__ import unicode_literals

from pyramid.view import view_config, view_defaults

from pyramid.compat import ascii_native_

from pyramid.httpexceptions import (
    HTTPNotFound
)

from pyramid_skosprovider.utils import (
    parse_range_header
)

import logging
log = logging.getLogger(__name__)


class RestView(object):

    def __init__(self, request):
        self.request = request
        self.skos_registry = self.request.skos_registry


@view_defaults(renderer='skosjson', accept='application/json')
class ProviderView(RestView):

    @view_config(route_name='skosprovider.conceptschemes', request_method='GET')
    def get_conceptschemes(self):
        return [{'id': p.get_vocabulary_id()} for p in self.skos_registry.get_providers()]

    @view_config(route_name='skosprovider.conceptscheme', request_method='GET')
    def get_conceptscheme(self):
        scheme_id = self.request.matchdict['scheme_id']
        provider = self.skos_registry.get_provider(scheme_id)
        if not provider:
            return HTTPNotFound()
        return {'id': provider.get_vocabulary_id()}

    @view_config(route_name='skosprovider.conceptscheme.cs', request_method='GET')
    def get_conceptscheme_concepts(self):
        scheme_id = self.request.matchdict['scheme_id']
        provider = self.skos_registry.get_provider(scheme_id)
        if not provider:
            return HTTPNotFound()
        query = {}
        mode = self.request.params.get('mode', 'default')
        label = self.request.params.get('label', None)
        postprocess = False
        if mode == 'dijitFilteringSelect' and label == '':
            concepts = []
        else:
            if label not in [None, '*', '']:
                if mode == 'dijitFilteringSelect' and '*' in label:
                    postprocess = True
                    query['label'] = label.replace('*', '')
                else:
                    query['label'] = label
            type = self.request.params.get('type', None)
            if type in ['concept', 'collection']:
                query['type'] = type
            coll = self.request.params.get('collection', None)
            if coll is not None:
                query['collection'] = {'id': coll, 'depth': 'all'}
            concepts = provider.find(query)
        # We need to refine results further
        if postprocess:
            if label.startswith('*') and label.endswith('*'):
                concepts = [c for c in concepts if label[1:-1] in c['label']]
            elif label.endswith('*'):
                concepts = [c for c in concepts if c['label'].startswith(label[0:-1])]
            elif label.startswith('*'):
                concepts = [c for c in concepts if c['label'].endswith(label[1:])]
        # Result paging
        paging_data = False
        if 'Range' in self.request.headers:
            paging_data = parse_range_header(self.request.headers['Range'])
        count = len(concepts)
        if not paging_data:
            paging_data = {
                'start': 0,
                'finish': count - 1 if count > 0 else 0,
                'number': count
            }
        cslice = concepts[paging_data['start']:paging_data['number']]
        self.request.response.headers[ascii_native_('Content-Range')] = \
            ascii_native_('items %d-%d/%d' % (
                paging_data['start'], paging_data['finish'], count
            ))
        return cslice

    @view_config(route_name='skosprovider.c', request_method='GET')
    def get_concept(self):
        scheme_id = self.request.matchdict['scheme_id']
        concept_id = self.request.matchdict['c_id']
        provider = self.skos_registry.get_provider(scheme_id)
        concept = provider.get_by_id(concept_id)
        if not concept:
            return HTTPNotFound()
        return concept
