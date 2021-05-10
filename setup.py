from os import path
from setuptools import setup, find_packages

about_path = path.join(path.dirname(path.abspath(__file__)), 'hopcolony', '__about__.py')
about = {}
with open(about_path) as fp:
    exec(fp.read(), about)

setup(
    name=about['__title__'],
    version=about['__version__'],
    description='Hopcolony Python SDK',
    long_description='HopColony SDK to communicate with backend for Python developers',
    url=about['__url__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    license=about['__license__'],
    keywords='hopcolony core cloud development backend',
    install_requires=[
        "requests==2.22.0",
        "parsel==1.6.0",
        "typer==0.3.2",
        "pyyaml==5.3.1",
        "click-spinner==0.1.10",
        "tabulate==0.8.7",
        "beautifulsoup4==4.9.3",
        "pika==1.2.0",
        "selenium==3.141.0",
        "simple-term-menu==0.10.5",
        "psutil==5.8.0",
        "webdriver-manager==3.3.0",
        "kubernetes==12.0.1"
    ],
    packages=find_packages(),
    python_requires='>=3.5',
    entry_points={
        "console_scripts": [
            "hopctl=hopcolony.__main__:main",
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
    ],
)