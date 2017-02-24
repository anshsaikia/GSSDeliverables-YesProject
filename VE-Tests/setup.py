# from distutils.core import setup
import os
import shutil

from setuptools import find_packages, setup  # from pytest plugin sample

setup(
    name='ve_test_utils',
    version='1.0',
    packages=find_packages(exclude=['tests.*', 'tests', '*.tests', '*.tests.*', 'conftest*', 'docs', 'build']),
    install_requires=[
        'configparser',
        'Appium-Python-Client',
        'bunch',
        'pytest',
        'pytz',
        'python-dateutil',
        'python-jsonrpc',
        'requests',
        'setuptools',
        'web.py',
        'enum',
        'enum34',
        'suds==0.4',
        'pytest-repeat',
    ],
    package_data={'Language': ['IH_VE_Translation.xlsm']},
    # dependency_links=[
    #     'git+https://stash-eng-rtp1.cisco.com/stash/scm/campnou/iex_client.git#egg=iex_client-0.1',
    #     'git+https://github.com/mikeage/fabric.git#egg=fabric-1.10.3'
    # ],
    # entry_points={'pytest11': ['vgw = pytest_vgw.fixtures']},
    url='http://gitlab.cisco.com/campnou/vgw_test_utils/tree/master',
    license='Copyright Cisco 2016',
    author='zhamilton',
    author_email='zhamilton@cisco.com',
    description='lib support for android/ios based E2E tests and fixtures',
    zip_safe=False
)
