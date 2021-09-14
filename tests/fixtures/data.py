# -*- coding: utf8 -*-

from skosprovider.providers import (
    DictionaryProvider
)

from skosprovider.skos import (
    ConceptScheme,
    Label
)

larch = {
    'id': 1,
    'uri': 'http://python.com/trees/larch',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'The Larch'},
        {'type': 'prefLabel', 'language': 'nl', 'label': 'De Lariks'},
        {'type': 'sortLabel', 'language': 'nl', 'label': 'c'}
    ],
    'notes': [
        {'type': 'definition', 'language': 'en', 'note': 'A type of tree.'}
    ],
    'sources': [
        {'citation': 'Monthy Python. Episode Three: How to recognise different types of trees from quite a long way away.'}
    ],
    'matches': {
        'close': ['http://id.python.org/different/types/of/trees/nr/1/the/larch']
    }
}

chestnut = {
    'id': 2,
    'uri': 'http://python.com/trees/chestnut',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'The Chestnut'},
        {'type': 'altLabel', 'language': 'nl', 'label': 'De Paardekastanje'},
        {'type': 'sortLabel', 'language': 'nl', 'label': 'a'}
    ],
    'notes': [
        {
            'type': 'definition', 'language': 'en',
            'note': 'A different type of tree.'
        }
    ],
    'matches': {
        'related': ['http://id.python.org/different/types/of/trees/nr/17/the/other/chestnut']
    }
}

species = {
    'id': 3,
    'uri': 'http://python.com/trees/species',
    'labels': [
        {'type': 'prefLabel', 'language': 'en', 'label': 'Trees by species'},
        {'type': 'altLabel', 'language': 'en', 'label': 'Trees by their species'},
        {'type': 'prefLabel', 'language': 'nl', 'label': 'Bomen per soort'},
        {'type': 'prefLabel', 'language': 'nl', 'label': 'b'}
    ],
    'notes': [
        {
            'type': 'scopeNote', 'language': 'en',
            'note': 'A division of trees.'
        }
    ],
    'type': 'collection',
    'members': ['1', '2']
}

trees = DictionaryProvider(
    {'id': 'TREES', 'default_language': 'nl'},
    [larch, chestnut, species],
    concept_scheme=ConceptScheme(
        uri='http://python.com/trees',
        labels=[
            Label('Different types of trees', 'prefLabel', 'en'),
            Label('Verschillende soorten bomen', 'prefLabel', 'nl')
        ]
    )
)
