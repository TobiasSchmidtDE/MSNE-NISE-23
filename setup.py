from setuptools import setup, find_packages

setup(
    name="emg_game",
    version="0.1.0",
    python_requires=">=3.8.0",
    packages=find_packages(exclude=("tests",)),
)
