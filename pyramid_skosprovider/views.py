# -*- coding: utf8 -*-

from pyramid_skosprovider import get_skos_registry

from pyramid.view import view_config, view_defaults


class RestView(object):

    def __init__(self, request):
        self.request = request

@view_defaults(renderer='json', accept='application/json')
class ProviderView(RestView):

    @view_config(route_name='skosprovider.conceptscheme', request_method='GET')
    def get_conceptscheme(self):
        scheme_id = self.request.matchdict['scheme_id']
        regis = get_skos_registry(self.request)
        providers = regis.get_providers(ids = [scheme_id])
        return providers[0].get_all()

    @view_config(route_name='skosprovider.concept', request_method='GET')
    def get_concept(self):
        scheme_id = self.request.matchdict['scheme_id']
        concept_id = self.request.matchdict['concept_id']
        regis = get_skos_registry(self.request)
        providers = regis.get_providers(ids = [scheme_id])
        return providers[0].get_by_id(concept_id)
