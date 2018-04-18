from setuptools import setup, find_packages
from wallabag_api import __version__ as version

install_requires = [
    'requests',
]

setup(
    name='wallabag_api',
    version=version,
    description='Wallabag API to add every pages you want to your Wallabag account',
    long_desc='Wallabag is a "read it later" service, and that Wallabag API allow you to save web pages '
              'to your own account',
    author='FoxMaSk',
    author_email='foxmask@trigger-happy.eu',
    url='https://github.com/push-things/wallabag_api',
    download_url="https://github.com/push-things/wallabag_api/archive/wallabag_api-" + version + ".zip",
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Communications',
    ],
    install_requires=install_requires,
    include_package_data=True,
)
