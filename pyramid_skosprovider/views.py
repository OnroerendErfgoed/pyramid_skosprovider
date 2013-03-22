# -*- coding: utf8 -*-

from pyramid_skosprovider import get_skos_registry

from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound
)

from pyramid_skosprovider.utils import (
    parse_range_header
)


class RestView(object):

    def __init__(self, request):
        self.request = request
        self.skos_registry = get_skos_registry(self.request)


@view_defaults(renderer='json', accept='application/json')
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

    @view_config(route_name='skosprovider.conceptscheme.concepts', request_method='GET')
    def get_conceptscheme_concepts(self):
        scheme_id = self.request.matchdict['scheme_id']
        provider = self.skos_registry.get_provider(scheme_id)
        if not provider:
            return HTTPNotFound()
        if 'label' in self.request.params and self.request.params.get('label') != '*':
            concepts = provider.find({
                'label': self.request.params.get('label')
            })
        else:
            concepts = provider.get_all()
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
        self.request.response.headers['Content-Range'] = \
            'items %d-%d/%d' % (paging_data['start'], paging_data['finish'], count)
        return cslice

    @view_config(route_name='skosprovider.concept', request_method='GET')
    def get_concept(self):
        scheme_id = self.request.matchdict['scheme_id']
        concept_id = self.request.matchdict['concept_id']
        regis = get_skos_registry(self.request)
        provider = self.skos_registry.get_provider(scheme_id)
        concept = provider.get_by_id(concept_id)
        if not concept:
            return HTTPNotFound()
        return concept
