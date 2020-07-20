# -*- coding: utf8 -*-
'''
This module contains function for rendering SKOS objects to JSON.
'''

from pyramid.renderers import JSON

from skosprovider.skos import (
    ConceptScheme,
    Concept,
    Collection,
    Label,
    Note,
    Source
)

from skosprovider.jsonld import (
    jsonld_c_dumper,
    jsonld_conceptscheme_dumper,
)

import logging
log = logging.getLogger(__name__)

json_renderer = JSON()


def concept_adapter(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider.skos.Concept` to json.

    :param skosprovider.skos.Concept obj: The concept to be rendered.
    :rtype: :class:`dict`
    '''
    p = request.skos_registry.get_provider(obj.concept_scheme.uri)
    language = request.params.get('language', request.locale_name)
    label = obj.label(language)
    return {
        'id': obj.id,
        'type': 'concept',
        'uri': obj.uri,
        'label': label.label if label else None,
        'concept_scheme': {
            'uri': obj.concept_scheme.uri,
            'labels': obj.concept_scheme.labels
        },
        'labels': obj.labels,
        'notes': obj.notes,
        'sources': obj.sources,
        'narrower': _map_relations(obj.narrower, p, language),
        'broader': _map_relations(obj.broader, p, language),
        'related': _map_relations(obj.related, p, language),
        'member_of': _map_relations(obj.member_of, p, language),
        'subordinate_arrays':  _map_relations(obj.subordinate_arrays, p, language),
        'matches': obj.matches
    }


def collection_adapter(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider.skos.Collection` to json.

    :param skosprovider.skos.Collection obj: The collection to be rendered.
    :rtype: :class:`dict`
    '''
    p = request.skos_registry.get_provider(obj.concept_scheme.uri)
    language = request.params.get('language', request.locale_name)
    label = obj.label(language)
    return {
        'id': obj.id,
        'type': 'collection',
        'uri': obj.uri,
        'label': label.label if label else None,
        'concept_scheme': {
            'uri': obj.concept_scheme.uri,
            'labels': obj.concept_scheme.labels
        },
        'labels': obj.labels,
        'notes': obj.notes,
        'sources': obj.sources,
        'members': _map_relations(obj.members, p, language),
        'member_of': _map_relations(obj.member_of, p, language),
        'superordinates':  _map_relations(obj.superordinates, p, language),
        'infer_concept_relations': obj.infer_concept_relations
    }


def _map_relations(relations, p, language='any'):
    '''
    :param: :class:`list` relations: Relations to be mapped. These are
        concept or collection id's.
    :param: :class:`skosprovider.providers.VocabularyProvider` p: Provider
        to look up id's.
    :param string language: Language to render the relations' labels in
    :rtype: :class:`list`
    '''
    ret = []
    for r in relations:
        c = p.get_by_id(r)
        if c:
            ret.append(_map_relation(c, language))
        else:
            log.warning(
                'A relation references a concept or collection %d in provider %s that can not be found. Please check the integrity of your data.' %
                (r, p.get_vocabulary_id())
            )
    return ret


def _map_relation(c, language='any'):
    """
    Map related concept or collection, leaving out the relations.

    :param c: the concept or collection to map
    :param string language: Language to render the relation's label in
    :rtype: :class:`dict`
    """
    label = c.label(language)
    return {
        'id': c.id,
        'type': c.type,
        'uri': c.uri,
        'label': label.label if label else None
    }


def label_adapter(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider.skos.Label` to json.

    :param skosprovider.skos.Label obj: The label to be rendered.
    :rtype: :class:`dict`
    '''
    return {
        'label': obj.label,
        'type': obj.type,
        'language': obj.language
    }


def note_adapter(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider.skos.Note` to json.

    :param skosprovider.skos.Note obj: The note to be rendered.
    :rtype: :class:`dict`
    '''
    return {
        'note': obj.note,
        'type': obj.type,
        'language': obj.language,
        'markup': obj.markup
    }


def source_adapter(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider.skos.Source` to json.

    :param skosprovider.skos.Source obj: The source to be rendered.
    :rtype: :class:`dict`
    '''
    return {
        'citation': obj.citation,
        'markup': obj.markup
    }


json_renderer.add_adapter(Concept, concept_adapter)
json_renderer.add_adapter(Collection, collection_adapter)
json_renderer.add_adapter(Label, label_adapter)
json_renderer.add_adapter(Note, note_adapter)
json_renderer.add_adapter(Source, source_adapter)


jsonld_renderer = JSON()


def conceptscheme_ld_adapter(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider.skos.ConceptScheme` to jsonld.

    :param skosprovider.skos.ConceptScheme obj: The conceptscheme to be rendered.
    :rtype: :class:`dict`
    '''
    p = request.skos_registry.get_provider(obj.uri)
    language = request.params.get('language', request.locale_name)
    request.response.content_type = 'application/ld+json'
    context = request.route_url('skosprovider.context')
    return jsonld_conceptscheme_dumper(p, context, language=language)


def concept_ld_adapter(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider.skos.Concept` to jsonld.

    :param skosprovider.skos.Concept obj: The concept to be rendered.
    :rtype: :class:`dict`
    '''
    p = request.skos_registry.get_provider(obj.concept_scheme.uri)
    language = request.params.get('language', request.locale_name)
    request.response.content_type = 'application/ld+json'
    context = request.route_url('skosprovider.context')
    return jsonld_c_dumper(p, obj.id, context, language=language)


def collection_ld_adapter(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider.skos.Concept` to jsonld.

    :param skosprovider.skos.Concept obj: The concept to be rendered.
    :rtype: :class:`dict`
    '''
    p = request.skos_registry.get_provider(obj.concept_scheme.uri)
    language = request.params.get('language', request.locale_name)
    request.response.content_type = 'application/ld+json'
    context = request.route_url('skosprovider.context')
    return jsonld_c_dumper(p, obj.id, context, language=language)


jsonld_renderer.add_adapter(ConceptScheme, conceptscheme_ld_adapter)
jsonld_renderer.add_adapter(Concept, concept_ld_adapter)
jsonld_renderer.add_adapter(Collection, collection_ld_adapter)
