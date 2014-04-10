Installation
============

To install pyramid_skosprovider, use pip

.. code-block:: bash
    
    pip install pyramid_skosprovider


To activate pyramid_skosprovider, just include it.

.. code-block:: python

    config = Configurator()
    config.include('pyramid_skosprovider')

This will create a skosprovider.registry and add it to the pyramid application 
registry.
