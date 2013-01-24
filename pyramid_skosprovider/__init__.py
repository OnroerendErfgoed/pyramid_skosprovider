# -*- coding: utf8 -*-

from zope.interface import Interface

from skosprovider.registry import Registry


class ISkosRegistry(Interface):
    pass


def _build_skos_registry(registry):
    skos_registry = registry.queryUtility(ISkosRegistry)
    if skos_registry is not None:
        return skos_registry

    skos_registry = Registry()

    registry.registerUtility(skos_registry, ISkosRegistry)
    return registry.queryUtility(ISkosRegistry)


def get_skos_registry(registry):
    #Argument might be a config or request
    regis = getattr(registry, 'registry', None)
    if regis is None:
        regis = registry
    return regis.queryUtility(ISkosRegistry)


def includeme(config):
    _build_skos_registry(config.registry)
    config.add_directive('get_skos_registry', get_skos_registry)
