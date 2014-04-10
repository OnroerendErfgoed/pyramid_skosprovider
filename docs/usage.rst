Usage
=====

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
