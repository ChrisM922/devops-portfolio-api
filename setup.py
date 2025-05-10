from setuptools import setup, find_packages

setup(
    name="flask-todo",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask",
        "sqlalchemy",
        "psycopg2-binary",
    ],
) 