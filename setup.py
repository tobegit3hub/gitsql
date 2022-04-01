# Update the code and upload the package to pypi
# 1. python ./setup.py bdist_wheel --universal
# 2. twine upload dist/xxx.whl

from setuptools import setup, find_packages

setup(
    name="gitsql",
    version="0.1.0",
    author="tobe",
    author_email="tobeg3oogle@gmail.com",
    url="https://github.com/tobegit3hub/gitsql",
    description="Query Git with SQL",
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'openmldb>=0.4.2', 'openmldb_lab'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "gitsql=gitsql.cli:main"
        ],
    })
