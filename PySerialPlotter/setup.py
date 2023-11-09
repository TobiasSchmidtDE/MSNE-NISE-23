from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='PySerialPlotter',
    version='0.1.0',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pyserialplotter = main:run',  # This assumes you have a 'run' function in main.py to start the app
        ],
    },
)
