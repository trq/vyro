import os
import subprocess

class Package:

    def __init__(self, path):
        self.path = path
        # The last two fragments of a packages
        # path are the vendor and package name
        self.vendor, self.name = path.split('/')[-2:]

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
            fp = open(self.path + '/README.md', 'r')
            readme = fp.read()
            fp.close()
            return readme

    def provision(self):
        """
        Setup an enviroment where the package can have its provisioning
        scripts executed then execute them.

        See ./lib/bash/shell.sh
        """
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
