from setuptools import setup, find_packages
from wallabag_api import __version__ as version

install_requires = [
    'requests==2.18.4',
]

setup(
    name='wallabag_api',
    version=version,
    description='Wallabag API to add every pages you want to your Wallabag account',
    author='FoxMaSk',
    author_email='foxmask@trigger-happy.eu',
    url='https://github.com/foxmask/wallabag_api',
    download_url="https://github.com/foxmask/wallabag_api/archive/"
                 "wallabag_api-" + version + ".zip",
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet',
        'Topic :: Communications',
    ],
    install_requires=install_requires,
    include_package_data=True,
)
