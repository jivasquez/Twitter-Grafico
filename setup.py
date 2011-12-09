from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='Twitter grafico',
      version=version,
      description="Resumen gráfico de twitter",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='twitter gr\xc3\xa1fico im\xc3\xa1genes resumen',
      author='Juan Ignacio V\xc3\xa1squez',
      author_email='ji.vasquez0@gmail.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
