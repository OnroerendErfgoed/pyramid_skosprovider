Usage
=====

To get a :class:`skosprovider.registry.Registry` instance that 
was configured globally, call :func:`pyramid_skosprovider.get_skos_registry` 
with the current application registry. 

Eg. in a view:

.. code-block:: python

    from pyramid_skosprovider import get_skos_registry

    def my_view(request):
        skos = get_skos_registry(request.registry)
        providers = skos.get_providers()
        # ...

Since this only works for globally configured registries, it's not the preferred 
way. Alternatively you can get the registry as an attribute of a pyramid request:

.. code-block:: python

    def my_view(request):
        skos = request.skos_registry
        providers = skos.get_providers()
        # ...

For a real-world example of an integration of `pyramid_skosprovider` in a
`Pyramid` application, have a look at 
`Atramhasis <https://github.com/OnroerendErfgoed/atramhasis>`_, a SKOS vocabulary
editor partially built upon this library.
