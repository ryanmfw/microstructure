from distutils.core import setup

setup(
    name='MicroStructure',
    version='0.1.0',
    author='Ryan Wendt',
    author_email='ryan@ryanwendt.com',
    packages=['microstructure', 'microstructure.test'],
    scripts=[],
    url='http://pypi.python.org/pypi/MicroStructure/',
    license='LICENSE.txt',
    description='Market microstructure analysis tool',
    long_description=open('README.txt').read(),
    install_requires=[
       # "Django >= 1.1.1",
        #"caldav == 0.1.4",
        ],
    )