# TODO: consider removing this if traitlets config and refactor of package
#       makes this unnecessary
class ExpandConfigurator():
    """
    """
    # TODO: Do smarter. Some things have the same type (e.g. ancestor has the
    #       same stuff as content). Do by content type?

    # all is what's available to expand for a type. on is what's configured to
    # be on for expansion.
    EXPAND_CFG= {
        'content': {
            'all': [
                'ancestors', 'body', 'children', 'container', 'descendants',
                'history', 'metadata', 'operations', 'space', 'version',
            ],
            'on': [
                'ancestors', 'body', 'children', 'container', 'descendants',
                'history', 'metadata', 'operations', 'space', 'version',
            ],
        },
        'ancestors': {
            all': [
                'ancestors', 'body', 'children', 'container', 'descendants',
                'history', 'metadata', 'operations', 'space', 'version',
            ],
            'on': [
                'ancestors', 'body', 'children', 'container', 'descendants',
                'history', 'metadata', 'operations', 'space', 'version',
            ],
        },
        'body': {
            'all': [
                'anonymous_export_view', 'editor', 'export_view',
                'styled_view', 'storage', 'view',
            ],
            'on': [],
        },
        'children': {
            'all': ['attachment', 'comment', 'page',],
            'on': [],
        },
        'attachment': {
            all': [
                'ancestors', 'body', 'children', 'container', 'descendants',
                'history', 'metadata', 'operations', 'space', 'version',
            ],
            'on': [
                'ancestors', 'body', 'children', 'container', 'descendants',
                'history', 'metadata', 'operations', 'space', 'version',
            ],
        },
        'comment': {
            all': [
                'ancestors', 'body', 'children', 'container', 'descendants',
                'history', 'metadata', 'operations', 'space', 'version',
            ],
            'on': [
                'ancestors', 'body', 'children', 'container', 'descendants',
                'history', 'metadata', 'operations', 'space', 'version',
            ],
        },
        'page': {
            all': [
                'ancestors', 'body', 'children', 'container', 'descendants',
                'history', 'metadata', 'operations', 'space', 'version',
            ],
            'on': [
                'ancestors', 'body', 'children', 'container', 'descendants',
                'history', 'metadata', 'operations', 'space', 'version',
            ],
        },
        'container': {
            'all': ['description', 'homepage', 'icon',],
            'on': [],
        },
        'description': {
            'all': ['plain', 'view',],
            'on': [],
        },
        'homepage': {
            all': [
                'ancestors', 'body', 'children', 'container', 'descendants',
                'history', 'metadata', 'operations', 'space', 'version',
            ],
            'on': [
                'ancestors', 'body', 'children', 'container', 'descendants',
                'history', 'metadata', 'operations', 'space', 'version',
            ],
        },
        'descendants': {
            'all': ['attachment', 'comment', 'page',],
            'on': [],
        },
        'history': {
            'all': ['lastUpdated', 'nextVersion', 'previousVersion',],
            'on': [],
        },
        'metadata': {
            'all': ['currentuser', 'labels',],
            'on': [],
        },
        'currentuser': {
            'all': ['favourited', 'lastmodified', 'viewed',],
            'on': [],
        },
        'labels': {
            'all': [],
            'on': [],
        },
        'operations': {
            'all': [],
            'on': [],
        },
        'space': {
            'all': ['description', 'homepage', 'icon',],
            'on': [],
        },
        'version': {
            'all': [],
            'on': [],
        },
    }

    def __init__(self, *args, **kwargs):
        """
        """
        pass
