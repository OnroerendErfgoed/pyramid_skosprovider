# -*- coding: utf8 -*-

import re

from pyramid.renderers import JSON

from skosprovider.skos import (
    Concept,
    Collection,
    Label,
    Note
)

def parse_range_header(range):
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
    return {
        'id': obj.id,
        'type': 'concept',
        'label': obj.label().label,
        'labels': obj.labels,
        'notes': obj.notes,
        'narrower': obj.narrower,
        'broader': obj.broader,
        'related': obj.related
    }

def collection_adapter(obj, request):
    return {
        'id': obj.id,
        'type': 'collection',
        'label': obj.label().label,
        'labels': obj.labels,
        'members': obj.members
    }

def label_adapter(obj, request):
    return {
        'label': obj.label,
        'type': obj.type,
        'language': obj.language
    }

def note_adapter(obj, request):
    return {
        'note': obj.note,
        'type': obj.type,
        'language': obj.language
    }

json_renderer.add_adapter(Concept, concept_adapter)
json_renderer.add_adapter(Collection, collection_adapter)
json_renderer.add_adapter(Label, label_adapter)
json_renderer.add_adapter(Note, note_adapter)
