from setuptools import setup, find_packages

setup(
    name='web_form_integration',
    version='1.0.0',
    description='Custom app for web form and Twilio integration',
    author='SMS',
    author_email='shoaibshah1255@gmail.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'twilio'
    ]
)
