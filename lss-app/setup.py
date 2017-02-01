
from setuptools import setup, find_packages
import sys, os

setup(name='lss',
    version='1.0',
    description="LSS Test Tool",
    long_description="LSS Test Tool",
    classifiers=[],
    keywords='',
    author='Amith Devatha',
    author_email='amithdevatha1@gmail.com',
    url='',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        ### Required to build documentation
        # "Sphinx >= 1.0",
        ### Required for testing
        # "nose",
        # "coverage",
        ### Required to function
        'cement',
        ],
    setup_requires=[],
    entry_points="""
        [console_scripts]
        lss = lss.cli.main:main
    """,
    namespace_packages=[],
    )
