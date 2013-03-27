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

Exposed information
-------------------

This library takes your skosproviders and makes them available as REST services. 
The following API is planned:

 * GET `/conceptschemes`: Get all registered concept schemes.
 * GET `/conceptschemes/{scheme_id}`: Get information about a concept scheme.
 * GET `/conceptschemes/{scheme_id}/concepts`: Search for concepts in a scheme.
 * GET `/conceptschemes/{scheme_id}/concepts/{concept_id}`: Get information about a concept
 * GET `/concepts`: Search for concepts in one or more schemes.
 * GET `/concepts/{scheme_id}/{concept_id}`: Get information about a concept, 
   is an alias for `/conceptschemes/{scheme_id}/concepts/{concept_id}`.

.. _skosprovider: https://github.com/koenedaele/skosprovider
