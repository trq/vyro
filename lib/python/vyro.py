import pickle
import os
import subprocess

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
        """
        Provision either  alist of packages if one is
        supplied, or all currently enabled packages.
        """
        if self.opts['<package>']:
            packages = self.opts['<package>']
        else:
            packages = self.util.get_enabled()

        for package in packages:
            self.__provision_package(package)

    def __provision_package(self, package):
        """
        Setup an enviroment where a package can have its provisioning
        scripts executed then execute them.

        See ./lib/bash/shell.sh
        """
        shell = os.path.dirname(__file__) + '/../bash/shell.sh'
        if os.path.exists(shell):
            vendor, package, path = self.util.resolve_package(package)
            if os.path.exists(path):
                subprocess.call([
                    'bash',                         # bash
                    shell,                          # command
                    'provision',                    # action
                    os.path.dirname(__file__),      # lib directory
                    os.getcwd(),                    # project directory
                    "%s:%s" % (vendor, package),    # vendor:package name
                    path                            # path to package
                ])

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
            vendor, package = self.util.resolve_package(package)[:2]
            if not os.path.islink(package):
                os.symlink("/vagrant/.vyro/repo/%s/%s" % (vendor, package), package)

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
        vendor, package = self.util.resolve_package(self.opts['<package>'][0])[:2]
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
            print "%s='%s'" % (key.upper(), value)

    def readme(self):
        """
        Display the contents of the README.md file belonging to a particular package.
        """
        vendor, package, path = self.util.resolve_package(self.opts['<package>'][0])
        path += "/README.md"
        if os.path.exists(path):
            readme = open(path, 'r')
            print readme.read()
            readme.close()

    def fetch(self):
        """
        Clone a package repo from github
        """
        vendor = self.opts['<vendor>']
        path = "%s/.vyro/repos/%s" % (os.getcwd(), vendor)
        url = "https://github.com/%s/vyro-packages.git" % vendor
        if not os.path.exists(path):
            try:
                subprocess.check_output(['git', 'clone', url, path], stderr=subprocess.STDOUT, shell=True);
            except subprocess.CalledProcessError as e:
                print "Unable to fetch " + url
        else:
            print "This vendor already exists"

    def test(self):
        print self.util.resolve_package(self.opts['<package>'][0]);

class Util:

    def __init__(self, opts):
        self.opts = opts

    def resolve_package(self, package):
        """
        Resolves a package into a [vendor, package, path] list.

        Resolution can be done by passing either of the following strings;
            "package"
            "vendor:package"
            "/path/to/vendor/package"

        If a package name alone is passed, we first check to see if this
        package is enabled, if so, we resolve that particular package. Otherwise,
        we will resolve a package from within the default vendor repository (if it exists).

        TODO: A resolved package should likely by an object type.
        """
        if os.path.isdir(package):
            path     = package
            parts    = package.split('/')
            package  = parts.pop()
            vendor   = parts.pop()
            resolved = [vendor, package]
        else:
            resolved = package.split(':')
            if len(resolved) < 2:
                path = "%s/.vyro/enabled/%s" % (os.getcwd(), resolved[0])
                if os.path.islink(path):
                    path     = os.readlink(path)
                    parts    = path.split('/')
                    package  = parts.pop()
                    vendor   = parts.pop()
                    resolved = [vendor, package]
                else:
                    path = "%s/.vyro/repo/default/%s" % (os.getcwd(), resolved[0])
                    if os.path.isdir(path):
                        resolved[:0] = ['default']

        vendor, package = resolved
        path = "%s/.vyro/repos/%s/%s" % (os.getcwd(), vendor, package)
        resolved.append(path)

        return resolved

    def requires(self, path):
        """
        Creates a required path if it doesn't already exist
        """
        path = os.getcwd() + '/' + path
        if not os.path.isdir(path):
            os.makedirs(path)

    def get_config(self, vendor, package, config = {}):
        """
        Retrieve a config option from a package
        """
        path = "%s/.vyro/repos/%s/%s" % (os.getcwd(), vendor, package)
        if os.path.exists(path):
            path += '/.config'
            if os.path.exists(path):
                config_file = open(path, 'r')
                config = pickle.load(config_file)
                config_file.close()

        return config

    def put_config(self, vendor, package, config):
        """
        Save a config option against a package
        """
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
