"""CLI tests for lss."""

from lss.utils import test

class CliTestCase(test.TestCase):
    def test_lss_cli(self):
        argv = ['--foo=bar']
        with self.make_app(argv=argv) as app:
            app.run()
            self.eq(app.pargs.foo, 'bar')
