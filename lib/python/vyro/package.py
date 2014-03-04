import os
import subprocess
import md5
import json
from vyro.state import env

class Package:

    def __init__(self, path):
        self.path = path
        # The last two fragments of a packages
        # path are the vendor and package name
        self.vendor, self.name = path.split('/')[-2:]

        self.__readme = None
        self.__config = None

    def __eq__(self, other):
        """
        Comparison used to see if two packages provide the same "package"
        """
        return self.name == other.name

    def __hash(self):
        """
        Get the hash of the package.sh file.

        # [todo] Hash needs to be extended to take into account config.json as well.
        """
        package_path = self.path + '/package.sh'
        if os.path.exists(package_path):
            with open(self.path + '/package.sh', 'r') as fp:
                contents = fp.read()
            fp.closed

            return md5.new(contents).hexdigest()

    def __cache(self):
        """
        Add this package to the "provisioned" cache.
        """
        with open(env.paths.cache + '/' + self.name + '.hash', 'w') as fp:
            fp.write(self.__hash())
        fp.closed

    def __is_cached(self):
        """
        Is this package in the "provisioned" cache?
        """
        if not os.path.exists(env.paths.cache + '/' + self.name + '.hash'):
            return False

        with open(env.paths.cache + '/' + self.name + '.hash', 'r') as fp:
            contents = fp.read()
        fp.closed

        return contents == self.__hash()

    def get_config(self):
        if not self.__config:
            self.__config = Config(self.vendor, self.name, self.path)

        return self.__config

    @property
    def readme(self):
        """
        Return the contents of the package README.md as a string.
        """
        path = self.path + '/README.md'
        if os.path.exists(path):
            if not self.__readme:
                with open(self.path + '/README.md', 'r') as fp:
                    self.__readme = fp.read()
                fp.closed

            return self.__readme

    def provision(self):
        """
        Setup an enviroment where the package can have its provisioning
        scripts executed then execute them.

        See ./lib/bash/shell.sh
        """
        if not self.__is_cached():
            lib_dir = "{path}/../../".format(path=os.path.dirname(__file__))  # lib directory
            shell = lib_dir + '/bash/shell.sh'
            subprocess.call([
                'bash',                                                         # bash
                shell,                                                          # command
                'provision',                                                    # action
                lib_dir,                                                        # lib directory
                os.getcwd(),                                                    # project directory
                "{vendor}:{name}".format(vendor=self.vendor, name=self.name),   # vendor:package name
                self.path                                                       # path to package
            ])
            self.__cache()

class Config(dict):

    def __init__(self, vendor, name, path):
        self.vendor = vendor
        self.name = name
        self.path = path
        self.__config = {}

        if os.path.exists(env.paths.conf + '/' + self.vendor + '.' + self.name + '.json'):
            with open(env.paths.conf + '/' + self.vendor + '.' + self.name + '.json', 'r') as fp:
                self.__config = json.load(fp)
            fp.closed
        elif os.path.exists(self.path + '/config.json'):
            with open(self.path + '/config.json', 'r') as fp:
                self.__config = json.load(fp)
            fp.closed

    def get(self, index):
        return self.__config.get(index)

    def dump(self):
        """
        Dump just the "config" index of the current config object
        to the screen as valid Bash code.
        """
        for option, data in self.__config.get('config').iteritems():
            if data.has_key('value'):
                value = data['value']
                if isinstance(value, bool):
                    if value == True:
                        value = 1
                    else:
                        value = 0
            else:
                value = None

            if value == 0:
                print option + '=0'
            elif value == 1:
                print option + '=1'
            else:
                print option + '="' + value + '"' if value else option + '='

    def list(self):
        """
        List available configuration options and there description
        """
        for option, data in self.__config.get('config').iteritems():
            print option,
            if data.has_key('description'):
                print '- ' + data['description']

    def set(self, key, val):
        """
        Set a configuration option
        """
        if key:
            if self.__config['config'].has_key(key):
                self.__config['config'][key]['value'] = val
            # [todo] - Should likely throw an exception here if key is invalid.

    def persist(self):
        """
        Persist the config option to the local vendor.package.json file.
        """
        with open(env.paths.conf + '/' + self.vendor + '.' + self.name + '.json', 'w') as fp:
            json.dump(self.__config, fp)
        fp.closed
