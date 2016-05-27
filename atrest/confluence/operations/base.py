# from traitlets import (
#     Type,
# )
#
# from atrest.core.operation import (
#     AtRESTOperationBase,
# )
#
# # from atrest.confluence.restclient import (
# #     ConfluenceRESTClient,
# # )
#
# class AtRESTConfluenceOperation(AtRESTOperationBase):
#     """
#     Base class for all AtREST Confluence REST API operations. An operation is
#     something that uses an API to make calls to a REST interface and does some
#     thing.
#
#     NOTE: Subclasses are not meant to be used on their own as a stand alone
#           application. An AtRESTClientBase subclass is needed to perform
#           operations. This is possible to put together, but it's not the
#           intent. This is meant to be used by AtRESTClientBase subclass
#           instantiations.
#     """
#
#     name = 'atrest-confluence-operation'
#
#     description = """AtREST base Confluence Operation that can be run
#     interactively.
#     TODO: Add more description...
#     """
#
#     examples = """
#     TODO: Add examples.
#     """
#
#     # TODO: Should this be passed in as needed rather than stored?.
#     # TODO: figure out how to import this
#     # apiclient = Type(ConfluenceRESTClient,
#     #     allow_none=True,
#     #     help='the confluence api client for the operation'
#     # )
#
#     def __init__(self, *args, **kwargs):
#         """
#         """
#         super().__init__(*args, **kwargs)
#         self.update_aliases({
#             'username' : 'AtRESTConfluenceOperation.username',
#             'apiurlbase' : 'AtRESTConfluenceOperation.api_url_base',
#         })
#
#     def initialize(self, *args, **kwargs):
#         """
#         Initialize the operation.
#         """
#         super().initialize(*args, **kwargs)
#
#     # start (and this start_interactive and _start_normal) should call a method
#     # where the magic should happen...
