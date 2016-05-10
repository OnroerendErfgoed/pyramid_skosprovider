# -*- coding: utf8 -*-
'''
This module contains a few utility functions.
'''

import re

import logging
log = logging.getLogger(__name__)

from pyramid.renderers import JSON

from skosprovider.skos import (
    Concept,
    Collection,
    Label,
    Note,
    Source
)


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

json_renderer = JSON()


def concept_adapter(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider.skos.Concept` to json.

    :param skosprovider.skos.Concept obj: The concept to be rendered.
    :rtype: :class:`dict`
    '''
    p = request.skos_registry.get_provider(obj.concept_scheme.uri)
    return {
        'id': obj.id,
        'type': 'concept',
        'uri': obj.uri,
        'label': obj.label().label if obj.label() else None,
        'concept_scheme': {
            'uri': obj.concept_scheme.uri,
            'labels': obj.concept_scheme.labels
        },
        'labels': obj.labels,
        'notes': obj.notes,
        'sources': obj.sources,
        'narrower': _map_relations(obj.narrower, p),
        'broader': _map_relations(obj.broader, p),
        'related': _map_relations(obj.related, p),
        'member_of': _map_relations(obj.member_of, p),
        'subordinate_arrays':  _map_relations(obj.subordinate_arrays, p),
        'matches': obj.matches
    }


def collection_adapter(obj, request):
    '''
    Adapter for rendering a :class:`skosprovider.skos.Collection` to json.

    :param skosprovider.skos.Collection obj: The collection to be rendered.
    :rtype: :class:`dict`
    '''
    p = request.skos_registry.get_provider(obj.concept_scheme.uri)
    return {
        'id': obj.id,
        'type': 'collection',
        'uri': obj.uri,
        'label': obj.label().label if obj.label() else None,
        'concept_scheme': {
            'uri': obj.concept_scheme.uri,
            'labels': obj.concept_scheme.labels
        },
        'labels': obj.labels,
        'notes': obj.notes,
        'sources': obj.sources,
        'members': _map_relations(obj.members, p),
        'member_of': _map_relations(obj.member_of, p),
        'superordinates':  _map_relations(obj.superordinates, p),
    }

def _map_relations(relations, p):
    '''
    :param: :class:`list` relations: Relations to be mapped. These are concept or collection id's.
    :param: :class:`skosprovider.providers.VocabularyProvider` p: Provider to look up id's.
    :rtype: :class:`list`
    '''
    ret = []
    for r in relations:
        c = p.get_by_id(r)
        if c:
            ret.append(_map_relation(c))
        else:
            log.warning(
                'A relation references a concept or collection %d in provider %s that can not be found. Please check the integrity of your data.' % 
                (r, p.get_vocabulary_id())
            )
    return ret

def _map_relation(c):
    """
    Map related concept or collection, leaving out the relations (to avoid circular dependencies)

    :param c: the concept or collection to map
    :rtype: :class:`dict`
    """
    return {
        'id': c.id,
        'type': c.type,
        'uri': c.uri,
        'label': c.label().label if c.label() else None
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
        'citation': obj.citation
    }


json_renderer.add_adapter(Concept, concept_adapter)
json_renderer.add_adapter(Collection, collection_adapter)
json_renderer.add_adapter(Label, label_adapter)
json_renderer.add_adapter(Note, note_adapter)
json_renderer.add_adapter(Source, source_adapter)
