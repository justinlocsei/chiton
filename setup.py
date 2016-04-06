from setuptools import find_packages, setup

setup(
    name='chiton',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
)
