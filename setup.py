from setuptools import setup

setup(
    name="orders",
    version="0.1",
    package_dir={"": "src"},
    packages=["domain", "app", "project"],
)
