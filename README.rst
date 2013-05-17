pyramid_skosprovider
====================

This library integrates skosprovider_ in a pyramid application.

.. image:: https://travis-ci.org/koenedaele/pyramid_skosprovider.png
        :target: https://travis-ci.org/koenedaele/pyramid_skosprovider

Installation
------------

To install pyramid_skosprovider, use pip

.. code-block:: bash
    
    pip install pyramid_skosprovider


Setup
-----

To activate pyramid_skosprovider

.. code-block:: python

    config = Configurator()
    config.include('pyramid_skosprovider')

This will create a skosprovider.registry and add it to the pyramid application 
registry.


Usage
-----

To get a skosprovider.registry instance, call get_skos_registry with the 
current application registry. 
Eg. in a view:

.. code-block:: python

    from pyramid_skosprovider import get_skos_registry

    def my_view(request):
        skos = get_skos_registry(request.registry)
        providers = skos.get_providers()
        # ...

Alternatively you can get the registry as an attribute of a pyramid request:

.. code-block:: python

    from pyramid_skosprovider import get_skos_registry

    def my_view(request):
        skos = request.skos_registry
        providers = skos.get_providers()
        # ...

REST Services
-------------

This library takes your skosproviders and makes them available as REST services. 
The following API is present:

 * GET `/conceptschemes`: Get all registered concept schemes.
 * GET `/conceptschemes/{scheme_id}`: Get information about a concept scheme.
 * GET `/conceptschemes/{scheme_id}/c`: Search for concepts or collections in 
   a scheme.
 * GET `/conceptschemes/{scheme_id}/c/{c_id}`: Get information about a concept 
   or collection.

.. _skosprovider: https://github.com/koenedaele/skosprovider
