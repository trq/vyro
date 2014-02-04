import pickle
import os

class Router:

    def __init__(self, opts):
        self.opts = opts

    def handle(self):

        methods = [
            'provision',
            'available',
            'enabled',
            'enable',
            'disable',
            'configure',
            'readme',
            'fetch',
            'test'
        ]

        for method in methods:
            if self.opts[method]:
                controller = Controller(self.opts)
                getattr(controller, method)()

class Controller:

    def __init__(self, opts):
        self.opts = opts
        self.util = Util(opts)

    def provision(self):
        print "This is provision"
        print self.opts

    def available(self):
        """
        Loop through all vendors and display a list
        of all currently available packages.
        """
        enabled   = self.util.get_enabled()
        available = self.util.get_available()
        for vendor in available:
            print vendor + ':'
            for pkg in available[vendor]:
                if pkg not in enabled: 
                    print pkg,

    def enabled(self):
        """
        Display a list of all currently enabled packages.
        """
        for pkg in self.util.get_enabled():
            print pkg,

    def enable(self):
        """
        Enable a list of packages.
        """
        self.util.requires('/.vyro/enabled')
        os.chdir(os.getcwd() + '/.vyro/enabled')

        for package in self.opts['<package>']:
            package = self.util.resolve_name(package)[1]
            if not os.path.islink(package):
                os.symlink('/vagrant/.vyro/enabled/' + package, package)

    def disable(self):
        """
        Disable a list of packages.
        """
        for package in self.opts['<package>']:
            path = os.getcwd() + '/.vyro/enabled/' + package
            if os.path.islink(path):
                os.remove(path)

    def configure(self):
        """
        Passed a key/value pair set and pickle it.
        Passed a key only, remove it from any existing configuration.

        Dump the new configuration to screen.
        """
        vendor, package = self.util.resolve_name(self.opts['<package>'][0])
        if self.opts['<key>'] and self.opts['<value>']:
            key, value = self.opts['<key>'], self.opts['<value>']
            config = self.util.get_config(vendor, package)
            config[key] = value
            self.util.put_config(vendor, package, config)

        elif self.opts['<key>']:
            key = self.opts['<key>']
            config = self.util.get_config(vendor, package)
            if config.has_key(key):
                config.pop(key)
                self.util.put_config(vendor, package, config)
        
        config = self.util.get_config(vendor, package)
        for key, value in config.iteritems():
            print "%s = %s" % (key, value)

    def readme(self):
        """
        Display the contents of the README.md file belonging to a particular package.
        """
        vendor, package = self.util.resolve_name(self.opts['<package>'][0])
        path = "%s/.vyro/repos/%s/%s/README.md" % (os.getcwd(), vendor, package)
        if os.path.exists(path):
            readme = open(path, 'r')
            print readme.read()
            readme.close()

    def fetch(self):
        print "This is fetch"
        print self.opts

class Util:

    def __init__(self, opts):
        self.opts = opts

    def resolve_name(self, package):
        """
        Resolves a vendor:package name combination taking into
        account any default vendor when none is supplied
        """
        package = package.split(':')
        if len(package) < 2:
            package[:0] = ['default']

        return package

    def requires(self, path):
        """
        Creates a required path if it doesn't already exist
        """
        path = os.getcwd() + '/' + path
        if not os.path.isdir(path):
            os.makedirs(path)

    def get_config(self, vendor, package, config = {}):
        path = "%s/.vyro/repos/%s/%s" % (os.getcwd(), vendor, package)
        if os.path.exists(path):
            path += '/.config'
            if os.path.exists(path):
                config_file = open(path, 'r')
                config = pickle.load(config_file)
                config_file.close()

        return config

    def put_config(self, vendor, package, config):
        path = "%s/.vyro/repos/%s/%s" % (os.getcwd(), vendor, package)
        if os.path.exists(path):
            path += '/.config'
            config_file = open(path, 'w')
            pickle.dump(config, config_file)
            config_file.close()

    def get_enabled(self):
        """
        Return all currently enabled packages.
        """
        path = os.getcwd() + '/.vyro/enabled'
        if os.path.exists(path):
            return os.listdir(path)

    def get_available(self):
        """
        Return all available packages index by the vendor that
        provides them. This function takes into account (and will
        not return) packages that are already enabled.
        """
        path = os.getcwd() + '/.vyro/repos'
        results = {}
        if os.path.exists(path):
            for vendor in os.listdir(path):
                vendor_path = path + '/' + vendor

                results[vendor] = []
                for package in os.listdir(vendor_path):
                    results[vendor].append(package)

            return results
