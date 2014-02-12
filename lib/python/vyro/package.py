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

        if os.path.exists(self.path + '/config.json'):
            with open(self.path + '/config.json', 'r') as fp:
                self.config = json.load(fp)
            fp.closed

    def __hash(self):
        package_path = self.path + '/package.sh'
        if os.path.exists(package_path):
            with open(self.path + '/package.sh', 'r') as fp:
                contents = fp.read()
            fp.closed

            return md5.new(contents).hexdigest()

    def __cache(self):
        with open(env.paths.cache + '/' + self.name + '.hash', 'w') as fp:
            fp.write(self.__hash())
        fp.closed

    def __is_cached(self):
        if not os.path.exists(env.paths.cache + '/' + self.name + '.hash'):
            return False

        with open(env.paths.cache + '/' + self.name + '.hash', 'r') as fp:
            contents = fp.read()
        fp.closed

        return contents == self.__hash()

    def has_readme(self):
        """
        Does this package have a README?
        """
        path = self.path + '/README.md'
        return os.path.exists(path)

    def readme(self):
        """
        Return the contents of the package README.md as a string.
        """
        if self.has_readme():
            with open(self.path + '/README.md', 'r') as fp:
                readme = fp.read()
            fp.closed
            return readme

    def provision(self):
        """
        Setup an enviroment where the package can have its provisioning
        scripts executed then execute them.

        See ./lib/bash/shell.sh
        """
        if not self.__is_cached():
            lib_dir = "%s/../../" % os.path.dirname(__file__)  # lib directory
            shell = lib_dir + '/bash/shell.sh'
            subprocess.call([
                'bash',                             # bash
                shell,                              # command
                'provision',                        # action
                lib_dir,                            # lib directory
                os.getcwd(),                        # project directory
                "%s:%s" % (self.vendor, self.name), # vendor:package name
                self.path                           # path to package
            ])
            self.__cache()
