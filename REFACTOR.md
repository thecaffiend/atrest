# Refactoring AtREST

## LEFTOFF
* Client base class implemented, and confluence client has been refactored.
 * Testing needed
 * consider something like AtREST.core for clientbase.py and a module for
   application base (subclass of traitlets.config.Application that provides
   functionality for InteractiveApplication - an application that runs via a
   cli menu or otherwise interactively).
* confluence rest client
 * add create_new_xxx methods (content, labels, attachments, etc)
 * move `_get_content_title` from atrest to this. rename and make public api
* each client should be an interactive app, and should be able to load commands
  as subcommands (e.g. Token for jupyterhub) or as commands available through
  it's cli.
* make examples dir and add an example Application for SpaceLister
* rename AtREST dir atrest (caps suck)
* add scripts dir, and script for (at least) atrest app and atrest -i
  (interactive) alias. python scripts that have no .py extension (again, look
  at jupyterhub). may just rename tools for that
* update README and other doc for updates
* use skeleton (cookiecutter?) to make pip installable/doc skeletons
* previous atrest.py is still around.
 * move contents that are command specific to command classes
 * atrest.py will become the traitlets application location when that starts
 * remove expand_configurator.py
* get configuration working
* tests...

## General Notes
* provide a set of supported operations (check content existence, copy content,
    etc), and a mechanism to add extension operations for users. these should
    either be composed of supported operations (with some kind of DSL to
    compose), or via a user plugin/script that extends some kind of
    ExtensionOperationBase class. Experiment. look at design patterns for
    allowing classes for actions (like copy page) so the actions can be
    pluggable, but that don't require the ConfluenceRESTClient to be used as a
    singleton. Also, need to protect the api from prying eyes since it has
    username/password info Look at jupyterhub (using traitlets) for
    configurable objects and Django (installed apps and custom management
    commands) for other extensibility ideas.
* traitlets (used heavily by ipython) makes configuration of objects and
  applications pretty cake. Use that.
* pagination - user configure option to always return all items or set a
    pagination limit. currently (confluence at least), if limit is an allowed
    value in a query and it is not set, confluence defaults to 25. If all_of
    (from the PythonConfluenceAPI package) is used, it does requests (using
    the default limit per query if not set), which means a bunch of requests
    potentially.
* smarter logging. configurable log levels, make it work in cli and notebook
* base classes and default command classes
 * bases for command, recursive command, etc
* confluence does not support getting full history for content yet. the
  previous and next versions can be retrieved, but you can't go anywhere from
  there. so maintaining history on copy and the like is not possible.

## Class Notes
* each API module needs a client class wrapping the api object.
* each client class should load set of commands (supported out of the box and user added/created)
* each object should inherit from Configurable in traitlets
* commands
 * each has a name, a configuration, help text, and full documentation
 * some do one thing to one poc
 * some recurse, visiting a piece of content and all sub content from there
  * all recursive commands should know how to walk content (and children) of
    a particular type
  * for each visited poc, a processing method should be called
 * since the api package tend to store username and password, the commands
    should have minimal access to that information.
 * commands should be told who their API provider is instead of asking for one.

## Command Notes
Commands listed below may be methods of the api client or may be commands
supported natively or by user extension.

* Confluence
 * Create space
 * Copy space
 * Archive space (e.g. save to html/pdf/etc and perhaps zip)
 * Update content (e.g. add entry to table). Allow templates for update
   formatting (e.g. like a table snippit to be used to add a row)
 * Content find and replace
 * List Spaces
 * Get pages in space
 * Copy content
  * Source information needed
   * space key and title of content to copy __OR__ id for content to copy
  * Destination information needed
    * space key and title of content to be parent __OR__ id for content to be parent
  * Can be recursive or not
  * Can copy attachments or not
  * Can copy comments or not
  * Can copy labels or not

## AtREST Package Layout

Notes for new package layout. Possible layout

* __AtREST__
 * app.py - traitlets application for AtREST. should work like the jupyterhub
   application. see the traitlets github repo for an example application.
   running interactively (like the current atrest_cli) should be one mode of
   operation
 * helpers.py (better name) - decorators for methods (like debug_log_call and handles_http_error)
 * __AtREST.confluence__ - Confluence REST API module
  * client.py - new location for the current ConfluenceRESTClient (in atrest.py)
  * __AtREST.confluence.commands__ (better name) - Command classes for confluence API (like PageCopier)
 * __AtREST.jira__ - JIRA REST API module
 * __AtREST.stash__ - Stash REST API module

## Acronyms
* poc - piece of content
*
