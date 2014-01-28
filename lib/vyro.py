class Router:

    def handle(self, opts):
        controller = Controller()

        methods = [
            'provision', 'available', 'enabled', 'enable', 'disable', 'configure', 'readme', 'fetch'
        ]

        for method in methods:
            if opts[method]:
                #controller.__getattribute_(method)(opts)
                getattr(controller, method)(opts)

class Controller:

    def provision(self, opts):
        print opts

    def available(self, opts):
        print "This is available"
        print opts

    def enabled(self, opts):
        print "This is enabled"
        print opts

    def enable(self, opts):
        print "This is enable"
        print opts

    def disable(self, opts):
        print "This is disable"
        print opts

    def configure(self, opts):
        print "This is configure"
        print opts

    def readme(self, opts):
        print "This is readme"
        print opts

    def fetch(self, opts):
        print "This is fetch"
        print opts

    def help(self, opts):
        print "This is help"
        print opts
