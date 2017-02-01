"""LSS Test Tool base controller."""

from cement.ext.ext_argparse import ArgparseController, expose
import lss.cli.handler.AllStatsHandler as AllStatsHandler

class BaseController(ArgparseController):
    class Meta:
        label = 'base'
        description = 'LSS Test Tool'
        arguments = [
            (['-u', '--user'],
             dict(help='User Id', dest='user', action='store' ) ),
            (['-p', '--password'],
             dict(help='Password', dest='password', action='store' ) ),
            (['-e', '--environment'],
             dict(help='Terminate the script after X seconds default is 1800', dest='environment', action='store' ) ),
            (['-c', '--cam_id'],
             dict(help='Cam Id of the stream', dest='cam_id', action='store' ) ),
            (['-r', '--url'],
             dict(help='Url of the lss stream', dest='url', action='store',
                  metavar='URl') ),
            (['-i', '--interval'],
             dict(help='Time interval for sampling in seconds default is 10', dest='interval', action='store',
                  type=int, default=10) ),
            (['-t', '--terminate'],
             dict(help='Terminate the script after X seconds default is 1800', dest='terminate', action='store',
                  type=int, default=1800) ),
            ]

    @expose()
    def all_stats(self):
        a = AllStatsHandler.AllStatsHandler()
        a.calculate_stats(self.app)
