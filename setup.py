import os

from setuptools import setup


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('fuel_external_git/migrations')
extra_files += package_files('fuel_external_git/templates')
extra_files.append('settings.yaml')

setup(
    name='fuel_external_git',
    version='1.0',
    description='Nailgun extension which uses git repo for config files',
    author='Dmitry Ukov',
    author_email='dukov@mirantis.com',
    url='http://example.com',
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: Apache Software License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Environment :: Console',
                 ],
    packages=['fuel_external_git'],
    package_data={'fuel_external_git': extra_files},
    entry_points={
        'nailgun.extensions': [
           'fuel_external_git = fuel_external_git.extension:ExternalGit',
        ],
        'fuelclient': [
            'gitrepo_list = fuel_external_git.fuelclient:GitRepoList',
            'gitrepo_create = fuel_external_git.fuelclient:AddRepo',
            'gitrepo_delete = fuel_external_git.fuelclient:DeleteRepo',
            'gitrepo_update = fuel_external_git.fuelclient:UpdateRepo',
            'gitrepo_init = fuel_external_git.fuelclient:InitRepo',
            'gitrepo_get_configs = fuel_external_git.fuelclient:DownloadConfgs',
        ]
        },
    zip_safe=False,
)
