REST Services
=============

This library takes your skosproviders and makes them available as REST services. 
The following API is present:

 * GET `/conceptschemes`: Get all registered concept schemes.
 * GET `/conceptschemes/{scheme_id}`: Get information about a concept scheme.
 * GET `/conceptschemes/{scheme_id}/c`: Search for concepts or collections in 
   a scheme.
 * GET `/conceptschemes/{scheme_id}/c/{c_id}`: Get information about a concept 
   or collection.
