from distutils.core import setup
from setuptools import find_packages
setup(
    name='json2table',
    version='1.0',
    packages=find_packages(),
    package_dir={"json2table": "json2table"},
    description='Parse nested json object to table data',
    author='Chen Qingqing',
    author_email='chenqingqing0927@163.com',
    install_requires=['pandas', 'pymongo'],
    keywords=['json', 'flatten', 'pandas','table','csv']
)