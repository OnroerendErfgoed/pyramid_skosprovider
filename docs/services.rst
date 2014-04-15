====================
Service Documentation
====================

This library takes your skosproviders and makes them available as REST services. 
The pyramid_skosprovider serves JSON  as a REST service so it can be used easily inside a AJAX webbrowser call or by an external program.

The following API is present:

.. http:get:: /conceptschemes
    
    Get all registered conceptschemes.
    
    **Example request**:
    
    .. sourcecode:: http
    
        GET http://localhost:6543/conceptschemes
        -- response --
        200 OK
        Content-Length:  17

        Content-Type:  application/json; charset=UTF-8

        Date:  Mon, 14 Apr 2014 14:42:34 GMT

        Server:  waitress

        [{"id": "TREES"}]

   
.. http:get:: /conceptschemes/{scheme_id}
    
    Get information about a concept scheme.
    
    **Example request**:
    
    .. sourcecode:: http
    
        GET http://localhost:6543/conceptschemes/TREES

         -- response --
        200 OK
        Content-Length:  15

        Content-Type:  application/json; charset=UTF-8

        Date:  Mon, 14 Apr 2014 14:45:37 GMT

        Server:  waitress

        {"id": "TREES"}


    .. sourcecode:: http

        GET http://localhost:6543/conceptschemes/PLANTS

         -- response --
        404 Not Found
        Content-Length:  775

        Content-Type:  text/html; charset=UTF-8

        Date:  Tue, 15 Apr 2014 20:32:52 GMT

        Server:  waitress


		
.. http:get:: /conceptschemes/{scheme_id}/c
    
    Search for concepts or collections in a scheme.
    
    **Example request**:
    
    .. sourcecode:: http
    
        GET http://localhost:6543/conceptschemes/TREES/c


         -- response --
        200 OK
        Content-Length:  117

        Content-Range:  items 0-2/3

        Content-Type:  application/json; charset=UTF-8

        Date:  Mon, 14 Apr 2014 14:47:33 GMT

        Server:  waitress

        [{"id": "1", "label": "De Lariks"}, {"id": "2", "label": "De Paardekastanje"}, {"id": 3, "label": "Bomen per soort"}]

    .. sourcecode:: http

        GET http://localhost:6543/conceptschemes/PLANTS/c

         -- response --
        404 Not Found
        Content-Length:  775

        Content-Type:  text/html; charset=UTF-8

        Date:  Tue, 15 Apr 2014 20:32:52 GMT

        Server:  waitress

		
.. http:get:: /conceptschemes/{scheme_id}/c/{c_id}
    
    Get information about a concept or collection.
    
    **Example request**:
    
    .. sourcecode:: http
    
        GET http://localhost:6543/conceptschemes/TREES/c/1

        -- response --
        200 OK
        Content-Length:  316

        Content-Type:  application/json; charset=UTF-8

        Date:  Mon, 14 Apr 2014 14:49:27 GMT

        Server:  waitress

        {"broader": [], "narrower": [], "notes": [{"note": "A type of tree.", "type": "definition", "language": "en"}], "labels": [{"type": "prefLabel", "language": "en", "label": "The Larch"}, {"type": "prefLabel", "language": "nl", "label": "De Lariks"}], "type": "concept", "id": "1", "related": [], "label": "The Larch"}

    .. sourcecode:: http

        GET http://localhost:6543/conceptschemes/TREES/c/4

         -- response --
        404 Not Found
        Content-Length:  775

        Content-Type:  text/html; charset=UTF-8

        Date:  Tue, 15 Apr 2014 20:06:12 GMT

        Server:  waitress