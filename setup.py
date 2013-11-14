import os
import sys

sys.path.insert(0,'lib')
from setuptools import setup, find_packages

setup(
    name = "jnpr-wlc",
    version = "0.0.1",
    author = "Jeremy Schulman",
    author_email = "jschulman@juniper.net",
    description = ( "Juniper Wireless LAN Controller" ),
    license = "BSD-2",
    keywords = "Juniper wireless networking automation",
    url = "http://www.github.com/jeremyschulman/py-jnpr-wlc",
    package_dir={'':'lib'},    
    packages=find_packages('lib'),
    install_requires=[
        "lxml",
        "jinja2",
    ],
)
