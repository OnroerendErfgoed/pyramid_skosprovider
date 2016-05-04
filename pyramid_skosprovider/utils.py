# -*- coding: utf8 -*-
'''
This module contains a few utility functions.
'''

import re

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
        'narrower': [_map_relation(p.get_by_id(n)) for n in obj.narrower],
        'broader': [_map_relation(p.get_by_id(b)) for b in obj.broader],
        'related': [_map_relation(p.get_by_id(r)) for r in obj.related],
        'member_of': [_map_relation(p.get_by_id(m)) for m in obj.member_of],
        'subordinate_arrays':  [_map_relation(p.get_by_id(sa)) for sa in obj.subordinate_arrays],
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
        'members': [_map_relation(p.get_by_id(m)) for m in obj.members],
        'member_of': [_map_relation(p.get_by_id(m)) for m in obj.member_of],
        'superordinates':  [_map_relation(p.get_by_id(so)) for so in obj.superordinates],
    }


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
