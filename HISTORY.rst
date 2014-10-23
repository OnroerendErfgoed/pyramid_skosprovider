0.4.0 (2014-10-23)
------------------

- Compatibility with skosprovider 0.4.0
- Drop support for Python 2.6 and Python 3.2.
- Expose notes on collections.
- Expose matches on concepts (collections don't have matches).
- Expose subordinate_arrays on concepts and superordinates on collections.
- Integrate concept scheme information. Concepts and collections passed through 
  the service now contain the uri of the concept scheme they belong to. The 
  concept scheme endpoint now also exposes information like a uri, a list of 
  labels and notes.

0.3.0 (2014-06-24)
------------------

- Expose information about top concepts.
- Expose information about display top and display children.
- Fix a bug with returning concepts and collections not on the first page
  of data through the Range header. (#3)
- Added support for sorting. (#4, #5) [cedrikv]

0.2.0 (2014-05-14)
------------------

- Compatibility with skosprovider 0.3.0
- Added service documentation (#1)

0.1.1 (2014-04-10)
------------------

- Code coverage by coveralls.
- Removed unit tests from resulting package.
- Moved documentation to Sphinx.
- Reorganisation of tests.
- Changed to py.test as testrunner.
- Some Flake8 fixes.

0.1.0 (2013-05-16)
------------------

- Initial version
- Includes json views based on the interfaces skosprovider offers.
- Adds a skosprovider registry to the pyramid request.
