# -*- coding: utf8 -*-
'''
This module contains the pyramid views that expose services.
'''

from __future__ import unicode_literals

import itertools

from pyramid.view import view_config, view_defaults

from pyramid.compat import ascii_native_

from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPBadRequest
)

from pyramid_skosprovider.utils import (
    parse_range_header,
    QueryBuilder
)

import logging
log = logging.getLogger(__name__)


class RestView(object):

    def __init__(self, request):
        self.request = request
        self.skos_registry = self.request.skos_registry


@view_defaults(renderer='skosjson', accept='application/json')
class ProviderView(RestView):
    '''
    A set of views that expose information from a certain provider.
    '''

    @view_config(route_name='skosprovider.uri', request_method='GET')
    @view_config(route_name='skosprovider.uri.deprecated', request_method='GET')
    def get_uri(self):
        uri = self.request.params.get('uri', self.request.matchdict.get('uri', None))
        if not uri:
            return HTTPBadRequest()
        provider = self.skos_registry.get_provider(uri)
        if provider:
            return {
                'type': 'concept_scheme',
                'uri': provider.concept_scheme.uri,
                'id': provider.get_vocabulary_id()
            }
        c = self.skos_registry.get_by_uri(uri)
        if not c:
            return HTTPNotFound()
        return {
            'type': c.type,
            'uri': c.uri,
            'id': c.id,
            'concept_scheme': {
                'uri': c.concept_scheme.uri,
                'id': self.skos_registry.get_provider(c.concept_scheme.uri).get_vocabulary_id()
            }
        }

    @view_config(route_name='skosprovider.conceptschemes', request_method='GET')
    def get_conceptschemes(self):
        language = self.request.params.get('language', self.request.locale_name)
        return [
            {
                'id': p.get_vocabulary_id(),
                'uri': p.concept_scheme.uri,
                'label': p.concept_scheme.label(language).label if p.concept_scheme.label(language) else None,
                'subject': p.metadata['subject'] if p.metadata['subject'] else []
            } for p in self.skos_registry.get_providers()
        ]

    @view_config(route_name='skosprovider.conceptscheme', request_method='GET')
    def get_conceptscheme(self):
        scheme_id = self.request.matchdict['scheme_id']
        provider = self.skos_registry.get_provider(scheme_id)
        if not provider:
            return HTTPNotFound()
        language = self.request.params.get('language', self.request.locale_name)
        return {
            'id': provider.get_vocabulary_id(),
            'uri': provider.concept_scheme.uri,
            'label': provider.concept_scheme.label(language).label if provider.concept_scheme.label(language) else None,
            'subject': provider.metadata['subject'] if provider.metadata['subject'] else [],
            'labels': provider.concept_scheme.labels,
            'notes': provider.concept_scheme.notes,
            'sources': provider.concept_scheme.sources,
            'languages': provider.concept_scheme.languages
        }

    @view_config(route_name='skosprovider.conceptscheme.tc', request_method='GET')
    def get_conceptscheme_top_concepts(self):
        scheme_id = self.request.matchdict['scheme_id']
        provider = self.skos_registry.get_provider(scheme_id)
        if not provider:
            return HTTPNotFound()
        language = self.request.params.get('language', self.request.locale_name)
        return provider.get_top_concepts(language=language)

    @view_config(route_name='skosprovider.conceptscheme.display_top', request_method='GET')
    def get_conceptscheme_display_top(self):
        scheme_id = self.request.matchdict['scheme_id']
        provider = self.skos_registry.get_provider(scheme_id)
        if not provider:
            return HTTPNotFound()
        language = self.request.params.get('language', self.request.locale_name)
        return provider.get_top_display(language=language)

    def _build_providers(self, request):
        '''
        :param pyramid.request.Request request:
        :rtype: :class:`dict`
        '''
        # determine targets
        providers = {}
        ids = request.params.get('providers.ids', None)
        if ids:
            ids = ids.split(',')
            providers['ids'] = ids
        subject = self.request.params.get('providers.subject', None)
        if subject:
            providers['subject'] = subject
        return providers

    @view_config(route_name='skosprovider.cs', request_method='GET')
    def get_concepts(self):
        qb = QueryBuilder(self.request)
        query = qb()
        kwargs = {"language": qb.language, "providers": self._build_providers(self.request)}
        kwargs.update(self._get_sort_params())
        if qb.no_result:
            concepts = []
        else:
            concepts = self.skos_registry.find(query, **kwargs)
            # Flatten it all
            concepts = list(itertools.chain.from_iterable([c['concepts'] for c in concepts]))

        if qb.postprocess:
            concepts = self._postprocess_wildcards(concepts, qb.label)

        return self._page_results(concepts)

    @view_config(route_name='skosprovider.conceptscheme.cs', request_method='GET')
    def get_conceptscheme_concepts(self):
        scheme_id = self.request.matchdict['scheme_id']
        provider = self.skos_registry.get_provider(scheme_id)
        if not provider:
            return HTTPNotFound()
        qb = QueryBuilder(self.request)
        query = qb()
        kwargs = {"language": qb.language}
        kwargs.update(self._get_sort_params())
        if qb.no_result:
            concepts = []
        else:
            concepts = provider.find(query, **kwargs)

        if qb.postprocess:
            concepts = self._postprocess_wildcards(concepts, qb.label)

        return self._page_results(concepts)

    def _postprocess_wildcards(self, concepts, label):
        # We need to refine results further
        if label.startswith('*') and label.endswith('*'):
            concepts = [c for c in concepts if label[1:-1] in c['label']]
        elif label.endswith('*'):
            concepts = [c for c in concepts if c['label'].startswith(label[0:-1])]
        elif label.startswith('*'):
            concepts = [c for c in concepts if c['label'].endswith(label[1:])]
        return concepts

    def _get_sort_params(self):
        sort = self.request.params.get('sort', None)
        # Result sorting
        if sort:
            sort_order = 'desc' if sort[0:1] == '-' else 'asc'
            sort = sort[1:] if sort[0:1] in ['-', '+'] else sort
            sort = sort.strip().lower()  # dojo store does not encode '+'
            return {"sort": sort, "sort_order": sort_order}
        return {}

    def _page_results(self, concepts):
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
        cslice = concepts[paging_data['start']:paging_data['finish']+1]
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
        if not provider:
            return HTTPNotFound()
        concept = provider.get_by_id(concept_id)
        if not concept:
            return HTTPNotFound()
        return concept

    @view_config(route_name='skosprovider.c.display_children', request_method='GET')
    def get_concept_display_children(self):
        scheme_id = self.request.matchdict['scheme_id']
        concept_id = self.request.matchdict['c_id']
        provider = self.skos_registry.get_provider(scheme_id)
        if not provider:
            return HTTPNotFound()
        language = self.request.params.get('language', self.request.locale_name)
        children = provider.get_children_display(concept_id, language=language)
        if children is False:
            return HTTPNotFound()
        return children

    @view_config(route_name='skosprovider.c.expand', request_method='GET')
    def get_expand(self):
        scheme_id = self.request.matchdict['scheme_id']
        concept_id = self.request.matchdict['c_id']
        provider = self.skos_registry.get_provider(scheme_id)
        if not provider:
            return HTTPNotFound()
        expanded = provider.expand(concept_id)
        if not expanded:
            return HTTPNotFound()
        return expanded
