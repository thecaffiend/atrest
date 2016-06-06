"""
Traitlets classes for wrapping various types returned from confluence REST API
calls.
"""

from traitlets import (
    HasTraits, Integer, Instance, Unicode,
)


# TODO: break module this up in some way?

# TODO: How to handle expansion? e.g. if a page is requested and ancestors is
#       expanded, there will be an epand entry for it in the request, and the
#       response will have a list for ancestors in the content result, but
#       there is no indication in the response that it was expeanded (other
#       than the list being there and ancestors not existing in the result's
#       _expandable), so we wouldn't know to look for it out of the box. some
#       of the expandables will be lists of existing types (like ancestors
#       would be a list of content types), but some will be types not
#       implemented yet (like body.storage).

# TODO: Methods to return a representation suitable for creating new content

# TODO: Add classes:
#           * expandables
class ConfluenceTypeBase(HasTraits):
    """
    Base type for Confluence types. Defines methods usable by all subclasses
    for converting to/from confluence REST representations.

    Subclasses defining traits of their own should tag the traits with a
    json_key if the trait name differs from what is used in the Confluence
    json format.
    """
    def from_conf_format(self, conf_frmt):
        """
        Sets the values of the traits in the class to the ones from conf_frmt
        where the keys in conf_frmt are the json_key's for the trait name.
        """
        [
            self.set_trait_pair(tn, conf_frmt.get(self.json_key(tn), None)) for
                tn in self.trait_names()
        ]

    def to_conf_format(self):
        """
        Return a dict of json_keys for traits to values of the traits
        themselves if the trait json_key and value are truthy.
        """
        return {
            k: v for k, v in [
                self.get_trait_pair(tn) for tn in self.trait_names()
            ] if k and v
        }

    def get_trait_pair(self, trait_name):
        """
        Return a tuple of the json key for a trait name and the current value
        of the trait. If the trait is not defined, a tuple of (None, None) is
        returned
        """
        if self.has_trait(trait_name):
            trt = getattr(self, trait_name)
            return (
                self.json_key(trait_name),
                trt.to_conf_format() if hasattr(trt, 'to_conf_format') else trt
            )

        return (None, None)

    def set_trait_pair(self, trait_name, val):
        """
        """
        if self.has_trait(trait_name):
            trt = getattr(self, trait_name)
            trt.from_conf_format(val) if hasattr(
                trt, 'from_conf_format') else setattr(self, trait_name, val)

    def json_key(self, trait_name):
        """
        Returns the json_key for a trait. The trait should be tagged at
        definition with the key. E.g.

        trt = Unicode().tag(json_key='key_string')

        If the trait has not been tagged in this manner, the trait_name will be
        returned, thus the tagging is only necessary for traits with json keys
        that differ from the trait's name (e.g. in the event that the json
        key would be a reserved word in python and the trait name must be
        changed as a result).
        """
        return self.trait_metadata(trait_name, 'json_key') or trait_name

class Extensions(ConfluenceTypeBase):
    """
    Represents a Confluence extensions value type
    """
    # TODO: either add all possible extension values here as traits (defaulting
    #       to None) and only assign values to needed ones, or perhaps make
    #       extensions (and other things that change per content type)
    #       nested classes in the classes that use them?

    # from pages
    position = Unicode(None, allow_none=True).tag(json_key='position')

    # from attachments
    media_type = Unicode(None, allow_none=True).tag(json_key='mediaType')
    files_size = Integer(None, allow_none=True).tag(json_key='fileSize')
    comment = Unicode(None, allow_none=True).tag(json_key='comment')


class Links(ConfluenceTypeBase):
    """
    Represents a Confluence _links value type
    """

    # from pages
    webui = Unicode(None, allow_none=True).tag(json_key='webui')
    tinyui = Unicode(None, allow_none=True).tag(json_key='tinyui')
    self_link = Unicode(None, allow_none=True).tag(json_key='self')

    # from attachments
    download = Unicode(None, allow_none=True).tag(json_key='download')

    # from results lists (TODO: should this be here? RL is in another file)
    base = Unicode(None, allow_none=True).tag(json_key='base')
    context = Unicode(None, allow_none=True).tag(json_key='context')


class Expandable(ConfluenceTypeBase):
    """
    Represents a Confluence _expandable value type
    """
    # TODO: see todo in extensions. all possible or base class.
    container = Unicode(None, allow_none=True).tag(json_key='container')
    metadata = Unicode(None, allow_none=True).tag(json_key='metadata')
    operations = Unicode(None, allow_none=True).tag(json_key='operations')
    children = Unicode(None, allow_none=True).tag(json_key='children')
    history = Unicode(None, allow_none=True).tag(json_key='history')
    ancestors = Unicode(None, allow_none=True).tag(json_key='ancestors')
    body = Unicode(None, allow_none=True).tag(json_key='body')
    version = Unicode(None, allow_none=True).tag(json_key='version')
    descendants = Unicode(None, allow_none=True).tag(json_key='descendants')
    space = Unicode(None, allow_none=True).tag(json_key='space')


class DescriptionRepresentation(ConfluenceTypeBase):
    """
    Represents a Confluence description representation value type.
    """
    value = Unicode(None, allow_none=True).tag(json_key='value')
    representation = Unicode(None, allow_none=True).tag(json_key='representation')

class Description(ConfluenceTypeBase):
    """
    Represents a Confluence description value type.
    """
    representation = Instance(klass=DescriptionRepresentation, kw={}).tag(json_key='plain')


class Space(ConfluenceTypeBase):
    """
    Represents a Confluence space value type. This type would be returned from
    a call to PythonConfluenceAPI.get_space_information for example.
    """
    conf_id = Unicode(None, allow_none=True).tag(json_key='id')
    space_key = Unicode(None, allow_none=True).tag(json_key='key')
    name = Unicode(None, allow_none=True).tag(json_key='name')
    links = Instance(klass=Links, kw={}).tag(json_key='_links')
    description = Instance(klass=Description, kw={}).tag(json_key='description')

class Content(ConfluenceTypeBase):
    """
    Represents a Confluence content value type. There are a couple of different
    content types (e.g. 'page' and 'blogpost') available.
    """
    CONTENT_TYPES = {'page', 'blogpost', 'comment', 'attachment'}
    CONTENT_STATUS = {'current',}

    conf_id = Unicode(None, allow_none=True).tag(json_key='id')
    content_type = Unicode(None, allow_none=True).tag(json_key='type')
    status = Unicode(None, allow_none=True).tag(json_key='status')
    title = Unicode(None, allow_none=True).tag(json_key='title')
    extensions = Instance(klass=Extensions, kw={}).tag(json_key='extensions')
    links = Instance(klass=Links, kw={}).tag(json_key='_links')
    expandable = Instance(klass=Expandable, kw={}).tag(json_key='_expandable')


class Metadata(ConfluenceTypeBase):
    """
    Represents a Confluence metadata value type. These are found in attachment
    results as an example.
    """
    # from attachments
    media_type = Unicode(None, allow_none=True).tag(json_key='mediaType')
    comment = Unicode(None, allow_none=True).tag(json_key='comment')

# LEFTOFF
