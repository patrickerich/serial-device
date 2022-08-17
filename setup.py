from setuptools import setup
from setuptools import find_packages
import os
import serial_device

version = serial_device.__version__


def read_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='serial-device',
    version=version,
    description='Connect and communicate with serial devices',
    url='https://github.com/patrickerich/serial-device',
    license='MIT',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author='Patrick Erich',
    author_email='patrick.erich@pm.me',
    packages=find_packages(),
    python_requires='>=3.5',  # ??
    install_requires=['pyserial', ],
    # entry_points={},
    platforms='any',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
    ],
    zip_safe=False
)
