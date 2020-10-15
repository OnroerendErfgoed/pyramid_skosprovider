# -*- coding: utf8 -*-

from zope.interface import Interface

from skosprovider.registry import Registry

from pyramid_skosprovider.renderers import (
    json_renderer,
    jsonld_renderer
)

from pyramid.path import (
    DottedNameResolver
)


class ISkosRegistry(Interface):
    pass


def _parse_settings(settings):
    defaults = {
        'skosregistry_location': 'registry',
    }
    args = defaults.copy()

    # string setting
    for short_key_name in ('skosregistry_location', 'skosregistry_factory'):
        key_name = "skosprovider.%s" % short_key_name
        if key_name in settings:
            args[short_key_name] = settings.get(key_name)

    return args


def _register_global_skos_registry(registry):
    '''
    Build a :class:`skosprovider.registry.Registry` and attach it to the
    Pyramid registry.

    :param registry: The Pyramid registry

    :rtype: :class:`skosprovider.registry.Registry`
    '''
    settings = _parse_settings(registry.settings)

    if 'skosregistry_factory' in settings:
        r = DottedNameResolver()
        skos_registry = r.resolve(settings['skosregistry_factory'])()
    else:
        skos_registry = Registry(instance_scope='threaded_global')

    registry.registerUtility(skos_registry, ISkosRegistry)
    return registry.queryUtility(ISkosRegistry)


def _register_request_skos_registry(request):
    '''
    Get the :class:`skosprovider.registry.Registry` attached to this request.

    :param request: The Pyramid request

    :rtype: :class:`skosprovider.registry.Registry`
    '''
    settings = _parse_settings(request.registry.settings)

    if 'skosregistry_factory' in settings:
        r = DottedNameResolver()
        skos_registry = r.resolve(settings['skosregistry_factory'])(request)
    else:
        skos_registry = Registry(instance_scope='threaded_thread')

    return skos_registry


def get_skos_registry(registry):
    '''
    Get the :class:`skosprovider.registry.Registry` attached to this pyramid
    application.

    :param registry: A Pyramid registry, request or config.

    :rtype: :class:`skosprovider.registry.Registry`
    '''
    # Argument might be a registry or have it as an attribute
    regis = getattr(registry, 'registry', None)
    if regis is None:
        regis = registry
    settings = _parse_settings(regis.settings)

    print(settings)

    if settings['skosregistry_location'] == 'registry':
        return regis.queryUtility(ISkosRegistry)
    else:
        raise RuntimeError('This is an older method that \
            is maintained for Backward Compatibility. It should \
            only be called for a global registry.')


def includeme(config):
    settings = _parse_settings(config.registry.settings)

    if settings['skosregistry_location'] == 'registry':
        _register_global_skos_registry(config.registry)
        config.add_request_method(
            get_skos_registry,
            'skos_registry',
            reify=True
        )
    else:
        config.add_request_method(
            _register_request_skos_registry,
            'skos_registry',
            reify=True
        )

    config.add_renderer('skosjson', json_renderer)
    config.add_renderer('skosjsonld', jsonld_renderer)

    config.add_directive('get_skos_registry', get_skos_registry)

    config.add_route(
        'skosprovider.context',
        '/jsonld/context/skos'
    )
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
        'skosprovider.conceptscheme.jsonld',
        '/conceptschemes/{scheme_id}.jsonld'
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
        'skosprovider.c.jsonld',
        '/conceptschemes/{scheme_id}/c/{c_id}.jsonld'
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
