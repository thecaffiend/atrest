# Atlassian REST API Testing Notebook
Repo for playing with the Atlassian REST APIs via Python.

### Dependencies
There is no requirements.txt for use with the conda environment yet. It will be
forthcoming. For now, here are the things:
* [Anaconda](https://www.continuum.io/why-anaconda) - For managing the Python3
  (3.5) environment and dependencies (Jupyter notebook, other pip packages,
  etc).
* IPython - Installed with Anaconda and absolutely required for all the Python
  things
* manual pip upgrade performed in the environment `pip install --upgrade pip`
* [PythonConfluenceAPI](https://github.com/pushrodtechnology/PythonConfluenceAPI)
  A Python wrapper for the REST API. Install (after activating the right
  environment) via pip `pip install --upgrade PythonConfluenceAPI`. As of the
  time of writing, this installs 0.0.1rc6 (latest without upgrade is 0.0.1rc4)
* future - `pip install 'future>=0.15.2,<1'` There is a specific version need,
  for PythonConfluenceAPI, and it doesn't come with the pip
  PythonConfluenceAPI. This is not the "right" way to do this, but it works so
  far

### General/CLI Usage
* To come

### Notebook Usage
_NOTE_: This is not up to date. Use CLI until it is.

* Make the environment (assuming Anaconda is installed and on the path)
`conda create --name atlassian_rest python=3 tornado jupyter notebook pep8`
* Activate the environment
`source activate atlassian_rest`
* Install new packages (as needed...should be documented here if not already)
`conda install --name atlassian_rest [packages]` or `pip install [packages]`
* Run notebook server (blocking) `jupyter notebook --port [port_num]`
* Load the notebook 'Atlassian REST API Sandbox'
* Have fun. Run the cells in order. Hopefully I'll have time to document things
  in the notebook better soon.

### General TODO
* Sphinx documentationify!
* Style (e.g. PEP8) checking
* Update the atrest_cli with newly supported operations (like deep copy of
    content and dry run vs real modes).
* move TODOs in code to here that make sense
* add atrest_cli usage doc to this README
* support other atlassian rest api's (jira, stash, etc)
* move to traitlets style configurable application (with subcommands) and
  configurable classes
* look at class hierarchy for bases/standard functionality, allow subclassing
  and configuration methods to add user defined functionality (perhaps also
  adding a base for recursive commands like deep copying that walks some node
  type and has visit methods).
* make library pip installable and allow usage of other pip installed commands

#### API TODOs / Planned Functional Additions
##### Confluence
* TODOs
 * get the expand strings handled better (configurable, different per content
   type, etc)
 * security on user password. even if getpass is used to get the password (so
   it isn't echoed when entered), when used to initialize the REST API,
   it is stored in that object (and is accessible in plain text via
   `RESTClient.__api.password`). This could theoretically cause problems in
   a notebook or other interactive environment where objects are inspectable
   when running. Additionally, the interface uses HTTPBasicAuth (in requests
   library), so if not used over https, everything is sent in plaintext over
   the wire...
 * break out class/package structure
 * support maintaining history of copied items (like pages, attachments, etc).
   this is not yet implemented in the real Confluence REST API (should be at
   `/rest/api/content/{id}/version)`.
 * support comments on copy attachments (kept in metadata field of the
   attachment instead of as a child type like for pages)
 * support CQL advanced search
* Operations to support
 * Create space
 * Copy space
 * Archive space
 * Copy content without recursing
 * Update content (e.g. add entry to table). Allow templates for update
   formatting (e.g. like a table snippit to be used to add a row)
 * Content find and replace
 * more...

##### JIRA (not yet supported)
* Nothing to see here...yet

##### Stash (not yet supported)
* Nothing to see here...yet

##### Other (not yet supported)
* Nothing to see here...yet


### Notes
#### AtREST
* Tested against Confluence 5.9.6
* Test the REST API is available with:
  `curl -u username [BASE_URL]/rest/api/content` where BASE_URL is something
  like: `https://[ATLASSIAN_SERVER]/confluence`. You'll be prompted for a
  password for user `username`. The response should be a bunch of content (
  pages and such).

#### Confluence API
* Expandable properties: Calls to the Confluence REST API (by any method) often
  allow for the use of [expansion of properties to return](https://developer.atlassian.com/confdev/confluence-rest-api/expansions-in-the-rest-api).
  For copying, creating and otherwise manipulating content, these are a
  necessity. Below are some notes on expandable properties (starting at the
  level of a response containing a content object). Note that when specifying
  them in the query, don't include the preceeding `content.`. This is for
  context and will not give expected results. The property is fillowed by a
  list of available expansion properties (kept in the `_expandable` object of
  a parent object).
 * content: 'ancestors', 'body', 'children', 'container', 'descendants',
            'history', 'metadata', 'operations', 'space', 'version'
 * content.ancestors: ancestors are more content objects, so they have
                      the same as content
 * content.body: 'anonymous_export_view', 'editor', 'export_view',
                 'styled_view', 'storage', 'view'
 * content.body.anonymous_export_view: XHTML for a page (somehow
                                       different from export_view...
                                       more research)
 * content.body.editor: XHTML for the editor for the content. perhaps
                        more useful stuff too...more research
 * content.body.export_view: XHTML for a page (somehow different from
                             anonymous_export_view...more research)
 * content.body.styled_view: XHTML for a page (including css, images,
                             and maybe more)...more research
 * content.body.storage: XHTML for a page, needed for POST operations
                         I think...more research
 * content.body.view: Same as body, but this may be needed for copying
                      the content elsewhere.
 * content.children: 'attachment', 'comment', 'page'
 * content.children.attachment: attachments are more content objects,
                                so they have the same as content. but
                                the `_links` for the attachment holds
                                the download link and extensions,
                                metadata, and title have useful values
                                as well (extensions have comments
                                about the attachment, e.g.)
 * content.children.comment: comments are more content objects, so
                             they have the same as content. but they
                             also have extensions that contain things
                             like resolutions to the comment
 * content.children.page: Need to find an example page value for a
                          comment to determine what it means
 * content.container: 'description', 'homepage', 'icon' - All appear to be
                      related to the space the content resides in
 * content.container.description: 'plain', 'view'
 * content.container.description.plain: Not sure about the values
                                        (representation and value)
 * content.container.description.view: Not sure about the values
                                       (representation and value)
 * content.container.homepage: another page type, so same as content. seems to
                               refer to the main page for the space
 * content.container.icon: info about the space icon
 * content.descendants: looks to be the same as content.children. No page
                        expandable though
 * content.history: 'lastUpdated', 'nextVersion', 'previousVersion' - Also info
                    about the page history
 * content.history.lastUpdated: Info abut the last update (who, what, etc)
 * content.history.nextVersion: Info abut the next version
 * content.history.previousVersion: Info abut the previous version (who, what,
                                    etc)
 * content.metadata: 'currentuser', 'labels' - Nothing else
 * content.metadata.currentuser: 'favorited', 'lastmodified', 'viewed' -
                                 Nothing else
 * content.metadata.currentuser.favourited: ???
 * content.metadata.currentuser.lastmodified: Info about the last modifying
                                              user and what they changed
 * content.metadata.currentuser.viewed: Info about when the current user last
                                        viewed the page
 * content.metadata.labels: Need an example page with labels to research this
 * content.operations: List of operations for the current page (perhaps that
                       the auth user can do?)...more research
 * content.space: Same as content.container above
 * content.version: Info about the current version of the page.

### References
* Atlassian [REST API docs](https://developer.atlassian.com/docs/atlassian-platform-common-components/rest-api-development)
* Confluence REST API package
    [pushrodtechnology's PythonConfluenceAPI](https://github.com/pushrodtechnology/PythonConfluenceAPI)
* Some concepts for page copying based on
    [grundic's confluence-page-copier](https://github.com/grundic/confluence-page-copier)
