import os
import subprocess
from vyro.package import Package
from vyro.state import env

class RootRepository:
    """
    The "root" repository, used to manage multiple "vendor" respositories
    """
    def __init__(self, path):
        self.path = path
        self.vendors = [];

    def get_vendors(self, force=False):
        """
        Retrieve a list of all vendors within this repo
        """
        if len(self.vendors) == 0 or force:
            path = self.path + '/' + env.names.repo_dir
            for vendor_name in os.listdir(path):
                vendor_repo = VendorRepository(path + '/' + vendor_name)
                self.vendors.append(vendor_repo)

        return self.vendors

    def get_vendor(self, vendor_name):
        """
        Retrieve a particular vendor by name
        """
        for vendor in self.get_vendors():
            if vendor.name == vendor_name:
                return vendor

    def resolve_package(self, package):
        """
        Attempt to retrieve a package by vendor:package name
        """
        name = package.split(':')
        if len(name) < 2:
            name[:0] = [env.default_repo]

        vendor_name, package_name = name

        vendor = self.get_vendor(vendor_name)
        if vendor:
            return vendor.get_package(package_name)

class VendorRepository:
    """
    The "vendor" repository, used to manage multiple "packages".
    """
    def __init__(self, path):
        self.path = path
        self.name, = path.split('/')[-1:]
        self.packages = []

    def get_packages(self):
        """
        Retrieve a list of all packages within this repo
        """
        if not self.packages:
            for package_name in os.listdir(self.path):
                package = Package(self.path + '/' + package_name)
                self.packages.append(package)

        return self.packages

    def get_package(self, package_name):
        """
        Retrieve a particular package by name
        """
        for package in self.get_packages():
            if package.name == package_name:
                return package

class StageRepository():
    """
    The "stage" repository, used to manage symlinks pointing
    to all the packages that are staged for provisioning.
    """
    def __init__(self, path):
        self.path = path
        self.packages = [];

    def get_packages(self):
        """
        Retrieve a list of all staged packages
        """
        if not self.packages:
            for package_name in os.listdir(self.path):
                package_path = os.readlink(self.path + '/' + package_name)
                package = Package(package_path)
                self.packages.append(package)

        return self.packages

    def get_package(self, package_name):
        """
        Retrieve a package by package name
        """
        if os.path.islink(self.path + '/' + package_name):
            package_path = os.readlink(self.path + '/' + package_name)
            return Package(package_path)

    def stage(self, package):
        """
        Stage a package for provisioning
        """
        os.chdir(self.path)
        if not os.path.exists(package.name):
            os.symlink(package.path, package.name)

    def unstage(self, package):
        """
        Un stage a package
        """
        os.chdir(self.path)
        if os.path.islink(package.name):
            os.remove(package.name)

class RemoteRepository():
    """
    The "remote" repository. A WIP.
    Currently used only to clone a remote repository from Github.
    """
    def __init__(self, name):
        self.name = name

    def persist(self):
        """
        Clone a package repo from github
        """
        path = "{root}/{repo}/{name}".format(root=env.paths.root, repo=env.names.repo_dir, name=self.name)
        url = "https://github.com/{vendor}/vyro-packages.git".format(vendor=self.name)
        if not os.path.exists(path):
            try:
                subprocess.check_output(['git', 'clone', url, path], stderr=subprocess.STDOUT, shell=True);
            except subprocess.CalledProcessError as e:
                print "Unable to fetch " + url
