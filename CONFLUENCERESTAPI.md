# Confluence REST API Notes
Notes taken when using and consuming data from the Confluence REST API
(specifically version 5.9.6). This includes notes on data formats, URL formats,
gotchas, limitations and the like.

## General
General notes taken during usage.

* Limiting results - without being told otherwise, CRA will return 25 results
  max per query (paginate results).
 * This is ok if it's the desired result. It can be cumbersome to get results,
   check the `_links` to see if there are more, and get more if needed.
 * PCA provides a convenience method to get all of the results back if that's
   better. It does this via a generator around the pagination. To reduce
   network calls, its probably a good idea to set a high limit and to use the
   all_of function if you want all (or a large a number of) results.
 * The limit to return can be set as desired, but too high a number errors out
   the CRA server with a HTTP 500. A limit of 1048576 was tried without killing
   it, but the return seems to be limited at limit=500 (that's what was
   returned with the 1048576 limit in the request.)
* Expansion - each endpoint has a default set of items it returns in the
  response. Most support passing an `expand` string to tell it to expand
  specific fields in the response. The available expandable items are in a
  response's `_expandable` object and via the same in the objects nested in a
  response.
 * empty ancestors (if they have been expanded) in a response for a requested
   page means the page is a root page (most likely of a of a space)

## Specific Endpoint Notes

* `baseurl/rest/api/space/KEY/content`: gets all the pages in a space. could be
  used to build up a content tree early (fewer requests) for some operations


## Confluence Query Language (CQL)
Unfortunately referred to as CQL (used by other things already, like the
cassandra query language), this is the means to do advanced searches. More info
can be found in the references below.

* The following were tested with PCA using the cql_str keyword arg and the PCA
  search_content method.
 * find page within space with title containing 'SpaceName' and title
   containing 'Part of Name of Pag' (should get N results):
      `"(space~'SpaceName' and  type='page' and title~'Part of Name of Pag')"`
 * find page within space titled 'SpaceName' and title 'Full Page Name' OR a
   page in the space named 'Space2' with the page title 'Home' (should get 2
   results if both exist):
      `"(space='SpaceName' and  type='page' and title='Full Page Name') OR (space='Space2' and type='page' and title='Home')"`

## Limitations/Gotchas

## Acronyms and Abbreviations
* __CRA__ - Confluence REST API
* __CQL__ - Confluence Quesry Language
* __PCA__ - PythonConfluenceAPI


## References
Links and such that may help you on your journey...

* [Confluence Developer Docs](https://developer.atlassian.com/confdev)
* [Confluence REST API docs](https://developer.atlassian.com/confdev/confluence-rest-api)
* [Confluence REST API spec](https://docs.atlassian.com/confluence/REST/latest/)
* [Confluence CQL and REST Docs](https://developer.atlassian.com/confdev/confluence-rest-api/advanced-searching-using-cql)
* [Expansion in the REST API](https://developer.atlassian.com/confdev/confluence-rest-api/expansions-in-the-rest-api)
* [Examples of using the REST API](https://developer.atlassian.com/confdev/confluence-rest-api/confluence-rest-api-examples)
* [PythonConfluenceAPI on github](https://github.com/pushrodtechnology/PythonConfluenceAPI)
