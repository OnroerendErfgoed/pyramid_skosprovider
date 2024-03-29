pyramid_skosprovider
====================

.. image:: https://img.shields.io/pypi/v/pyramid_skosprovider.svg
        :target: https://pypi.python.org/pypi/pyramid_skosprovider
.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.5795939.svg
        :target: https://doi.org/10.5281/zenodo.5795939
.. image:: https://app.travis-ci.com/OnroerendErfgoed/pyramid_skosprovider.svg?branch=develop
        :target: https://app.travis-ci.com/OnroerendErfgoed/pyramid_skosprovider
.. image:: https://coveralls.io/repos/github/OnroerendErfgoed/pyramid_skosprovider/badge.svg?branch=develop
        :target: https://coveralls.io/github/OnroerendErfgoed/pyramid_skosprovider?branch=develop
.. image:: https://scrutinizer-ci.com/g/OnroerendErfgoed/pyramid_skosprovider/badges/quality-score.png?b=develop
        :target: https://scrutinizer-ci.com/g/OnroerendErfgoed/pyramid_skosprovider/?branch=develop

----

.. image:: https://readthedocs.org/projects/pyramid-skosprovider/badge/?version=latest
        :target: http://pyramid-skosprovider.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status
.. image:: https://joss.theoj.org/papers/10.21105/joss.05040/status.svg
        :target: https://doi.org/10.21105/joss.05040

This library integrates skosprovider_ in a pyramid application.


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

.. _skosprovider: https://github.com/OnroerendErfgoed/skosprovider
