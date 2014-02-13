from vyro.repository import RootRepository, StageRepository, RemoteRepository
from vyro.state import env

class Router:

    def __init__(self, opts):
        self.opts = opts

    def handle(self):

        methods = [
            'provision', 'list', 'staged', 'stage',
            'unstage', 'configure', 'readme', 'fetch'
        ]

        for method in methods:
            if self.opts[method]:
                controller = Controller(self.opts)
                getattr(controller, method)()
                break

class Controller:

    def __init__(self, opts):
        self.opts = opts

    def __toggle_stage(self, enable=True):
        """
        Stage / unstage a list of packages
        """
        stage = StageRepository(env.paths.stage)
        for package_name in self.opts['<package>']:
            if enable:
                root = RootRepository(env.paths.root)
                package = root.resolve_package(package_name)
                if package:
                    stage.stage(package)
            else:
                package = stage.get_package(package_name)
                if package:
                    stage.unstage(package)

    def provision(self):
        """
        Provision a list of packages
        """
        root = RootRepository(env.paths.root)
        for package_name in self.opts['<package>']:
            package = root.resolve_package(package_name)
            if package:
                package.provision()

    def list(self):
        """
        List available packages by vendor
        """
        root = RootRepository(env.paths.root)
        stage = StageRepository(env.paths.stage)
        for vendor in root.get_vendors():
            print vendor.name + ":"
            for package in vendor.get_packages():
                if package not in stage.get_packages():
                    print package.name,

    def staged(self):
        """
        List staged packages
        """
        stage = StageRepository(env.paths.stage)
        for package in stage.get_packages():
            print package.name + ' -> ' + package.vendor + ':' + package.name 

    def stage(self):
        """
        Stage a list of packages
        """
        self.__toggle_stage()

    def unstage(self):
        """
        Unstage a list of packages
        """
        self.__toggle_stage(enable=False)

    def configure(self):
        root = RootRepository(env.paths.root)
        package = root.resolve_package(self.opts['<package>'][0])
        if self.opts['<key>'] and self.opts['<value>']:
            print "edit a config option"
        elif self.opts['<key>']:
            print "delete a config option"
        else:
            for option in package.config['config']:
                value = option['value'] if 'value' in option else option['default']
                print option['name'] + '="' + value + '"'

    def readme(self):
        root = RootRepository(env.paths.root)
        package = root.resolve_package(self.opts['<package>'][0])
        if package and package.has_readme():
            print package.readme()

    def fetch(self):
        vendor = RemoteRepository(self.opts['<vendor>'])
        vendor.persist()
