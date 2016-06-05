"""
"""

from traitlets import (
    HasTraits, Unicode, List, Integer, Instance,
)

from atrest.confluence.core.types import (
    Links, ConfluenceTypeBase,
)

class ResultList(HasTraits):
    """
    """
    results = List(default_value=list([]), trait=Instance(ConfluenceTypeBase))
    start = Integer(0)
    limit = Integer(500) # TODO: this should be the MAX_LIMIT constant (500 should be the value of that)
    size = Integer(0)
    links = Instance(klass=Links)

    # TODO: need a way to say what kind

    def __init__(self):
        """
        """
        self.links = Links()

    def from_conf_format(self, conf_frmt):
        """
        """
        self.start = int(conf_frmt['start'])
        self.limit = int(conf_frmt['limit'])
        self.size = int(conf_frmt['size'])
        self.links.from_conf_format(conf_frmt['_links'])
        self.results = self.parse_results(conf_frmt['results'])

    def to_conf_format(self):
        """
        """
        return {
            'results': [r.to_conf_format() for r in self.results],
            'start': self.start,
            'limit': self.limit,
            'size': self.size,
            '_links': self.links.to_conf_format()
        }

    def parse_results(seelf, results):
        """
        """
        raise NotImplementedError
