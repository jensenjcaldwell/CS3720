from setuptools import setup, find_packages



setup(
    name='MyModule',
    version='0.1.1',
    author='Jensen Caldwell',
    packages=find_packages(),
    description='A package for loading and analyzing CSV data using pandas.',
    author_email="10786608@uvu.edu",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
