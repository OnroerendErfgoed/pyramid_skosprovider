Installation
============

To install `pyramid_skosprovider`, use pip

.. code-block:: bash
    
    pip install pyramid_skosprovider


To activate `pyramid_skosprovider`, you need to include it and configure your
:class:`skosprovider.registry.Registry`. Older versions, before `0.9.0`,
attached the `registry` to the Pyramid application registry. Starting with
`0.9.0` it's possible and recommended to attach the skos registry to a request.
The old way is still allowed for backward compatibility, but should only be
used with local provider that store all their data in memory, such as a
:class:`skosprovider.providers.DictionaryProvider`. Future versions will remove
this way of working.

Since `0.9.0`, two new settings were added:

*skosprovider.skosregistry_location* deteremines where your registry lives in
the application. Currently two options are supported: `registry` or `request`.
The first attaches the :class:`skosprovider.registry.Registry` to the Pyramid
application registry as the Pyramid application is started. The second option
attaches the skos registry to the Pyramid request. This ensures every reqeust
has it's own registry.

*skosprovider.skosregistry_factory* allows you to specify a factory function
for instantiating the :class:`skosprovider.registry.Registry`. This function
will receive the Pyramid request as a first argument if you are using a
registry attached to a request. If you do specify a factory, an empty skos
registry will be created and used.

Please be aware that attaching a registry to the Pyramid application registry
was the only option before `0.9.0`. It is still supported because it makes
sense for a registry that only contains providers that load all their data in
memory on initialisation. Providers that require a database connection should
always be attached to a request.

Supposing you want to attach your registry to requests, you would configure
your application. A possible configuration for a `myskos` application would be:

.. code-block:: yaml

    skosprovider.skosregistry_location: request
    skosprovider.skosregistry_factory: myskos.skos.build_registry

To actually use `pyramid_skosprovider`, you still need to include it in your
pyramid application and write the factory function. In your Pyramid startup
function:

.. code-block:: python

    config = Configurator()
    config.include('pyramid_skosprovider')

This will instantiate the :class:`skosprovider.registry.Registry` using the 
configuration you have provided and make it available to your application.

Your `myskos.skos` python module should then contain a `build_registry`
function that receives a Pyramid request, creates the skos registry and
returns it:

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
