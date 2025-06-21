# setup.py
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')

setup(
    name='web_form_integration',  # must match folder name
    version='0.0.1',              # or import from __init__.py
    description='Twilio SMS Integration for ERPNext',
    author='Zikpro',
    author_email='shoaibshah1255@email.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
