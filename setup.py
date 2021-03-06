from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pyrrhic',
      version=version,
      description="A utility to help test HTTP APIs",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python http rest api',
      author='Dan Fairs',
      author_email='dan@fezconsulting.com',
      url='http://dist.fezconsulting.com/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      test_requires=[
        'nose',
        'mock',
      ],
      entry_points="""
      [console_scripts]
      pyr = pyrrhic.ui:console
      """,
      )
