pyramid_skosprovider
====================

This library integrates skosprovider_ in a pyramid application.

.. image:: https://travis-ci.org/koenedaele/pyramid_skosprovider.png
        :target: https://travis-ci.org/koenedaele/pyramid_skosprovider
.. image:: https://coveralls.io/repos/koenedaele/pyramid_skosprovider/badge.png?branch=master
        :target: https://coveralls.io/r/koenedaele/pyramid_skosprovider

.. image:: https://readthedocs.org/projects/pyramid-skosprovider/badge/?version=latest
        :target: https://readthedocs.org/projects/pyramid-skosprovider/?badge=latest
        :alt: Documentation Status
.. image:: https://badge.fury.io/py/pyramid_skosprovider.png
        :target: http://badge.fury.io/py/pyramid_skosprovider

Building the docs
-----------------

More information about this library can be found in `docs`. The docs can be 
built using `Sphinx <http://sphinx-doc.org>`_.

Please make sure you have installed Sphinx in the same environment where 
pyramid_skosprovider is present.

.. code-block:: bash

    # activate your virtual env
    $ pip install -r requirements.txt
    $ python setup.py develop
    $ cd docs
    $ make html

.. _skosprovider: https://github.com/koenedaele/skosprovider
