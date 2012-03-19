from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='twittergrafico',
      version=version,
      description="Resumen grafico de twitter",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='twitter grafico imagenes resumen',
      author='Juan Ignacio Vasquez',
      author_email='ji.vasquez0@gmail.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['bottle==0.10.6', 'mako>=0.4.1', 'webhelpers', 'httplib2', 'lxml', 'python-twitter', 'pymongo'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
