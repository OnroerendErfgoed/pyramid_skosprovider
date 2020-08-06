Installation
============

To install `pyramid_skosprovider`, use pip

.. code-block:: bash
    
    pip install pyramid_skosprovider


To activate `pyramid_skosprovider`, you need to include it and configure your
:class:`skosprovider.registry.Registry`. Older versions, before `0.9.0`,
attached the `skosregistry` to the Pyramid application registry. Starting with
`0.9.0` it's possible and recommended to attach the skos registry to a request.
The old way is still allowed for backward compatibility, but should only be
used with local providers that store all their data in memory, such as a
:class:`skosprovider.providers.DictionaryProvider`.

To maintain the old way and enable the new one, two new settings were added in
`pyramid_skosprovider` `0.9.0`:

*skosprovider.skosregistry_location* deteremines where your registry lives in
the application. Currently two options are supported: `registry` or `request`.
The first attaches the :class:`skosprovider.registry.Registry` to the Pyramid
application registry as the Pyramid application is started. The second option
attaches the skos registry to the Pyramid request. This ensures every request
has it's own registry.

*skosprovider.skosregistry_factory* allows you to specify a factory function
for instantiating the :class:`skosprovider.registry.Registry`. This function
will receive the Pyramid request as a first argument if you are using a
registry attached to a request. If you do not specify a factory, an empty skos
registry will be created and used.

Please be aware that attaching a registry to the Pyramid application registry
was the only option before `0.9.0`. It is still supported because it makes
sense for a registry that only contains providers that load all their data in
memory on initialisation. Providers that require a database connection should
always be attached to a request.

Supposing you want to attach your registry to requests, you would write some
configuration. A possible configuration for a `myskos` application would be:

.. code-block:: ini

    skosprovider.skosregistry_location: request
    skosprovider.skosregistry_factory: myskos.skos.build_registry

To actually use `pyramid_skosprovider`, you still need to include it in your
pyramid application and write the factory function. In your Pyramid startup
function:

.. code-block:: python

    config = Configurator()
    config.include('pyramid_skosprovider')

This will add some views and configuration. Every request will now contain a
`skos_registry` attribute. The first time this attribute is accessed, the
SKOS registy will be build for you, using the specified factory function.

Your `myskos.skos` python module should contain this factory function. In our
example config, we called it `build_registry`. This is a function that receives 
a Pyramid request, creates the skos registry and returns it:

.. code-block:: python

    from skosprovider.registry import Registry
    from skosprovider.providers import DictionaryProvider

    def build_registry(request):

        r = Registry(
            instance_scope='threaded_thread'
        )
        
        dictprovider = DictionaryProvider(
            {
                'id': 'TREES',
                'default_language': 'nl',
                'subject': ['biology'],
                'dataset': {
                    'uri': 'http://id.trees.org/dataset'
                }
            },
            [],
            uri_generator=UriPatternGenerator('http://id.trees.org/types/%s'),
            concept_scheme=ConceptScheme('http://id.trees.org')
        )
        r.register_provider(dictprovider)

        return r

This is a very simple example. A typical real-life application would have
several providers. Some of them might be DictionaryProviders, others might
reaf from rdf files and still others might read from a SQL Databases. If you're
using the `skosprovider_sqlalchemy` provider, you would attach your database
session maker to the request and then pass it on to the SQLAlchemy provider in
your factory function.

If you want to attach the SKOS registry to the Pyramid registry, and not the
request, you would have the following config:


.. code-block:: ini

    skosprovider.skosregistry_location: registry
    skosprovider.skosregistry_factory: myskos.skos.build_registry

The `build_registry` factory would be very similar, but it does not have acces
to the request. This makes it a bad fit for threaded web-servers and leads to
bugs. But something like a :class:`skosprovider.providers.DictionaryProvider`
wpuld be fine. The factory function is almost identical, but we would also set
the Registry instance_scope to `threaded_global`. This can alert providers that
register with the registry that they might not be compatible.
`

.. code-block:: python

    from skosprovider.registry import Registry
    from skosprovider.providers import DictionaryProvider

    def build_registry():

        r = Registry(
            instance_scope='threaded_global'
        )
        
        dictprovider = DictionaryProvider(
            {
                'id': 'TREES',
                'default_language': 'nl',
                'subject': ['biology'],
                'dataset': {
                    'uri': 'http://id.trees.org/dataset'
                }
            },
            [],
            uri_generator=UriPatternGenerator('http://id.trees.org/types/%s'),
            concept_scheme=ConceptScheme('http://id.trees.org')
        )
        r.register_provider(dictprovider)

        return r
