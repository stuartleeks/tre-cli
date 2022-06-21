#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

PROJECT = 'tre'

# Change docs/sphinx/conf.py too!
VERSION = '0.1'

try:
    long_description = open('README.md', 'rt').read()
except IOError:
    long_description = ''

setup(
    name=PROJECT,
    version=VERSION,

    description='Demo TRE CLI for AzureTRE',
    long_description=long_description,

    author='Stuart Leeks',
    author_email='stuartle@microsoft.com',

    # url='',
    # download_url='',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: Developers',
        'Environment :: Console',
    ],

    platforms=['Any'],

    scripts=[],

    provides=[],
    install_requires=['cliff'],

    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'tre = tre.main:main'
        ],
        'tre.cli': [
            'login = tre.commands.login:Login',
            'api = tre.commands.api_call:ApiCall',
            'workspace list = tre.commands.workspace:WorkspaceList',
            'workspace show = tre.commands.workspace:WorkspaceShow',
            'workspace operation list = tre.commands.workspace_operation:WorkspaceOperationList',
            'workspace operation show = tre.commands.workspace_operation:WorkspaceOperationShow',
            'workspace workspace-service list = tre.commands.workspace_workspace_service:WorkspaceWorkspaceServiceList',
        ],
    },

    zip_safe=False,
)
