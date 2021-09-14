pyramid_skosprovider
====================

This library integrates skosprovider_ in a pyramid application.

.. image:: https://img.shields.io/pypi/v/pyramid_skosprovider.svg
        :target: https://pypi.python.org/pypi/pyramid_skosprovider
.. image:: https://readthedocs.org/projects/pyramid-skosprovider/badge/?version=latest
        :target: https://readthedocs.org/projects/pyramid-skosprovider/?badge=latest
        :alt: Documentation Status

.. image:: https://app.travis-ci.com/koenedaele/pyramid_skosprovider.png
        :target: https://app.travis-ci.com/koenedaele/pyramid_skosprovider
.. image:: https://img.shields.io/coveralls/koenedaele/pyramid_skosprovider.svg
        :target: https://coveralls.io/r/koenedaele/pyramid_skosprovider
.. image:: https://scrutinizer-ci.com/g/koenedaele/pyramid_skosprovider/badges/quality-score.png?b=master
        :target: https://scrutinizer-ci.com/g/koenedaele/pyramid_skosprovider/?branch=master


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
