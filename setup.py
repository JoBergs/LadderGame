#encoding: utf-8 -*-
from setuptools import setup, find_packages

version = '1.0.0'

setup(
    name='Ladder Game',
    version=version,
    description='A Raspberry Pi implementation of the hardware based ladder game.',
    author=u'Your Name',
    author_email='your@email.com',
    url='https://https://github.com/JoBergs/LadderGame.git',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[ ]
)
