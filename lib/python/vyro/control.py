class Router:

    def __init__(self, opts):
        self.opts = opts

    def handle(self):

        methods = [
            'provision', 'available', 'enabled', 'enable',
            'disable', 'configure', 'readme', 'fetch'
        ]

        for method in methods:
            if self.opts[method]:
                controller = Controller(self.opts)
                getattr(controller, method)()
                break

class Controller:

    def __init__(self, opts):
        self.opts = opts

    def provision(self): pass
    def available(self): pass
    def enabled(self): pass
    def enable(self): pass
    def disable(self): pass
    def configure(self): pass
    def readme(self): pass
    def fetch(self): pass
