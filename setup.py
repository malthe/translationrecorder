__version__ = '1.0.1'

import os
import sys

try:
    from distribute_setup import use_setuptools
    use_setuptools()
except:  # doesn't work under tox/pip
    pass

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:  # doesn't work under tox/pip
    README = ''
    CHANGES = ''

install_requires = []

version = sys.version_info[:3]
if version < (2, 7, 0):
    install_requires.append("ordereddict")
    install_requires.append("unittest2")

setup(
    name="translationrecorder",
    version=__version__,
    description=("Records gettext translation messages and "
                 "synchronizes to message catalogs."),
    long_description="\n\n".join((README, CHANGES)),
    classifiers=[
       "Development Status :: 4 - Beta",
       "Intended Audience :: Developers",
       "Programming Language :: Python",
       "Programming Language :: Python :: 2",
       "Programming Language :: Python :: 2.5",
       "Programming Language :: Python :: 2.6",
       "Programming Language :: Python :: 2.7",
      ],
    author="Malthe Borch",
    author_email="mborch@gmail.com",
    license='BSD-like (http://repoze.org/license.html)',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
    )
