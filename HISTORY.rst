1.2.1 (2023-10-21)
------------------

- Update Pyramid dependency to 2.0.2
- Add a ReadTheDocs config file (#104)
- Better handling of rendering a list of conceptschemes when one is unreachable. 
  This ensures that most providers can be listed, but possibly with the
  URI as the label if the provider is unresponsive. (#101)

1.2.0 (2023-03-08)
------------------

- Add missing @context in JSON-lD context (#95)
- Drop support for Python 3.6 and 3.7, add support for 3.10 and 3.11

**Attention!** Querying for a uri with a path in the URL as opposed to a query
parameter has been deprecated since version 0.7.0 and will be removed in
the upcoming 2.0 release. Please make sure to update your code.

1.1.0 (2021-12-21)
------------------

- upgrade requirements (#88)
- add CITATION.cff (#91)

1.0.0 (2021-09-14)
------------------

- Drop support for Python 2. (#87)

0.9.2 (2021-01-21)
------------------

- Fix an issue with case insensitive search containing a wildcard. (#82)

0.9.1 (2020-10-19)
------------------

- Add download links to JSON-LD version of concept and conceptscheme to improve
  user experience. (#78)
- Remove pyup. (#79)
- Update soms development dependencies.

0.9.0 (2020-08-06)
------------------

- Support running a registry per request, as opposed to per application as
  before. (#44)
- Add the `infer_concept_relations` attribute to the collection renderer. (#73)
- Add JSON-LD output to the REST service. (#63)
- Add support for match and match_type search parameters to search for concepts
  that match a certain URI and optionally have a certain type. (#68)
- Drop support for Python 3.4, add support for 3.7 and 3.8. This is the last version
  that will support Python 2. (#66)
- Remove the JSON renderers from the utils module.

0.8.0 (2017-07-12)
------------------

- Return an HTTP 404 response when a conceptscheme could not be found. (#24)
- Add universal wheel distribution. (#23)
- Add support for sorting on a SortLabel. This means a client can now ask to
  sort the results either on `id`, `label` or `sortlabel`. See the
  `skosprovider` docs for more on the `sortlabel`. This basically allows for
  arbitrary sorting per language so it's possible to eg. sort Historical
  periods chronologically. (#26) [cahytinne] 

0.7.0 (2016-08-11)
------------------

- Sort case insensitive when sorting by label. This is a BC break, although 
  to most users it might actually be a bug fix. (#16) [TalissaJoly]
- Add the markup attribute to Note json representations. This is a new addition
  to skosprovider 0.6.0 that allows marking that a note contains some markup
  (currently only HTML).
- Looking for a certain URI is now done with a query parameter in stead of in
  the path of a resource. So, `/uris/urn:x-skosprovider:trees` should now be
  called as `/uris?uri=urn:x-skosprovider:trees`. The old way is deprecated. It
  will still function under version `0.7.0`, but will be removed in a future
  version. (#19)
- Add support for the sources attribute, a new feature in skosprovider 0.6.0
- Add support for languages to Conceptschemes, a new feature in skosprovider
  0.6.0 that allows detailing what languages a conceptscheme uses.
- Move JSON renderers to their own file and fix some language handling issues.
  (#22)
- Add support for Python 3.5

0.6.0 (2015-03-02)
------------------

- Allow the client to specify in which language labels should preferentially
  be returned. This can be chosen by adding a ``language`` parameter to
  certain query strings. If not present, pyramid_skosprovider falls back on 
  pyramid's locale negotiation. (#10) (#14) [dieuska]
- Expose a provider's expand method. This returns the narrower transitive 
  closure for a certain concept or collection. (#11) [dieuska]
- Some documentation updates.

0.5.0 (2014-12-19)
------------------

- Conceptschemes expose information on the subject they're tagged with. [BartSaelen]
- A new search endpoint for searching across conceptschemes was added. Search
  syntax is the same as for searching within a single scheme, but the collection
  parameter is not accepted. Two extra parameters were added for limiting the
  search to a subset of available conceptschemes. (#8)
- A new endpoint for looking up a certain URI was added. This endpoint does not
  redirect to an external URI, but lets a client know where more information
  about this URI can be found (eg. in which conceptscheme a concept lives). (#7)

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
