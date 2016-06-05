"""
"""

from traitlets import (
    HasTraits, Instance, Unicode,
)

class ConfluenceTypeBase(HasTraits):
    """
    """

    def from_conf_format(self, conf_frmt):
        """
        """
        raise NotImplementedError

    def to_conf_format(self):
        """
        """
        # TODO: for these methods, give each class below a string for the key
        #       they should use for the conf_format (e.g. Links would have the
        #       key '_links')
        raise NotImplementedError

# TODO: move non-result classes (Links, Extensions, Expandable, etc) to another
#       module? they are resultbase extensions though...

class Extensions(ConfluenceTypeBase):
    """
    """
    position = Unicode('')

    def from_conf_format(self, conf_frmt):
        """
        """
        self.position = conf_frmt['position']

    def to_conf_format(self):
        """
        """
        return {
            'position': self.position
        }

class Links(ConfluenceTypeBase):
    """
    """
    webui = Unicode('')
    tinyui = Unicode('')
    self_link = Unicode('')

    def from_conf_format(self, conf_frmt):
        """
        """
        self.webui = conf_frmt['webui']
        self.tinyui = conf_frmt['tinyui']
        self.self_link = conf_frmt['self']

    def to_conf_format(self):
        """
        """
        return {
            'webui': self.webui,
            'tinyui': self.tinyui,
            'self': self.self_link
        }

class Expandable(ConfluenceTypeBase):
    """
    """
    # TODO: make expandable base class. this can't be the list for everything.
    #       too many things. perhaps each gets a Set of allowed values?
    container = Unicode('')
    metadata = Unicode('')
    operations = Unicode('')
    children = Unicode('')
    history = Unicode('')
    ancestors = Unicode('')
    body = Unicode('')
    version = Unicode('')
    descendants = Unicode('')
    space = Unicode('')

    def from_conf_format(self, conf_frmt):
        """
        """
        self.container = conf_frmt['container']
        self.metadata = conf_frmt['metadata']
        self.operations = conf_frmt['operations']
        self.children = conf_frmt['children']
        self.history = conf_frmt['history']
        self.ancestors = conf_frmt['ancestors']
        self.body = conf_frmt['body']
        self.version = conf_frmt['version']
        self.descendants = conf_frmt['descendants']
        self.space = conf_frmt['space']

    def to_conf_format(self):
        """
        """
        return {
            'container': self.container,
            'metadata': self.metadata,
            'operations': self.operations,
            'children': self.children,
            'history': self.history,
            'ancestors': self.ancestors,
            'body': self.body,
            'version': self.version,
            'descendants': self.descendants,
            'space': self.space
        }

class Content(ConfluenceTypeBase):
    CONTENT_TYPES = {'page', 'blogpost', 'comment', 'attachment'}
    CONTENT_STATUS = {'current',}

    # TODO: traits: Links, Expandable

    # LEFTOFF - will Nones hurt here?
    conf_id = Unicode('')
    content_type = Unicode('')
    status = Unicode('')
    title = Unicode('')
    extensions = Instance(klass=Extensions)
    links = Instance(klass=Links)
    expandable = Instance(klass=Expandable)

    def __init__(self, result=None):
        """
        """
        self.extensions = Extensions()
        self.links = Links()
        self.expandable = Expandable()

    def from_conf_format(self, conf_frmt):
        """
        """
        self.conf_id = conf_frmt['id']
        self.content_type = conf_frmt['type']
        self.status = conf_frmt['status']
        self.title  = conf_frmt['title']
        self.extensions.from_conf_format(conf_frmt['extensions'])
        self.links.from_conf_format(conf_frmt['_links'])
        self.expandable.from_conf_format(conf_frmt['_expandable'])

    def to_conf_format(self):
        """
        """
        return {
            'id': self.conf_id,
            'type': self.content_type,
            'status': self.status,
            'title': self.title,
            'extensions': self.extensions.to_conf_format(),
            '_links': self.links.to_conf_format(),
            '_expandable': self.expandable.to_conf_format()
        }
