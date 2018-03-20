# -*- coding: utf8 -*-

from zope.interface import Interface

from skosprovider.registry import Registry

from pyramid_skosprovider.utils import (
    json_renderer
)

from pyramid.path import (
    DottedNameResolver
)


class ISkosRegistry(Interface):
    pass


def _parse_settings(settings):
    defaults = {
        'skosregistry_location': 'registry',
        'skosregistry_factory': 'pyramid_skosprovider._skosregistry_factory',
    }
    args = defaults.copy()

    # string setting
    for short_key_name in ('skosregistry_location', 'skosregistry_factory'):
        key_name = "skosprovider.%s" % short_key_name
        if key_name in settings:
            args[short_key_name] = settings.get(key_name)

    return args


def _skosregistry_factory():
    return Registry()


def _build_skos_registry(settings):
    if 'skosregistry_factory' in settings:
        r = DottedNameResolver()
        skos_registry = r.resolve(settings['skosregistry_factory'])()
    else:
        skos_registry = Registry()
    return skos_registry


def _register_global_skos_registry(registry, settings):
    skos_registry = registry.queryUtility(ISkosRegistry)
    if skos_registry is not None:
        return skos_registry

    skos_registry = _build_skos_registry(settings)

    registry.registerUtility(skos_registry, ISkosRegistry)
    return registry.queryUtility(ISkosRegistry)


def get_global_skos_registry(registry):
    '''
    Get the :class:`skosprovider.registry.Registry` attached to this pyramid
    application.

    :rtype: :class:`skosprovider.registry.Registry`
    '''
    # Argument might be a config or request
    regis = getattr(registry, 'registry', None)
    if regis is None:
        regis = registry
    return regis.queryUtility(ISkosRegistry)


def get_request_skos_registry(request):
    '''
    Get the :class:`skosprovider.registry.Registry` attached to this request.

    :rtype: :class:`skosprovider.registry.Registry`
    '''
    settings = _parse_settings(request.registry.settings)
    skosregistry = _build_skos_registry(settings)
    return skosregistry


def includeme(config):
    settings = _parse_settings(config.registry.settings)

    if settings['skosregistry_location'] == 'registry':
        _register_global_skos_registry(config.registry, settings)
        config.add_request_method(get_global_skos_registry, 'skos_registry', reify=True)
    else:
        config.add_request_method(get_request_skos_registry, 'skos_registry', reify=True)

    config.add_renderer('skosjson', json_renderer)

    config.add_directive('get_skos_registry', get_global_skos_registry)

    config.add_route(
        'skosprovider.uri.deprecated',
        '/uris/{uri:.*}'
    )
    config.add_route(
        'skosprovider.uri',
        '/uris'
    )
    config.add_route(
        'skosprovider.cs',
        '/c'
    )
    config.add_route(
        'skosprovider.conceptschemes',
        '/conceptschemes'
    )
    config.add_route(
        'skosprovider.conceptscheme',
        '/conceptschemes/{scheme_id}'
    )
    config.add_route(
        'skosprovider.conceptscheme.cs',
        '/conceptschemes/{scheme_id}/c'
    )
    config.add_route(
        'skosprovider.conceptscheme.tc',
        '/conceptschemes/{scheme_id}/topconcepts'
    )
    config.add_route(
        'skosprovider.conceptscheme.display_top',
        '/conceptschemes/{scheme_id}/displaytop'
    )
    config.add_route(
        'skosprovider.c',
        '/conceptschemes/{scheme_id}/c/{c_id}'
    )
    config.add_route(
        'skosprovider.c.display_children',
        '/conceptschemes/{scheme_id}/c/{c_id}/displaychildren'
    )
    config.add_route(
        'skosprovider.c.expand',
        '/conceptschemes/{scheme_id}/c/{c_id}/expand'
    )

    config.scan()
