from setuptools import setup
import os

requires = ['pywifi', 'PySimpleGUI']
if os.name == 'nt':
    requires.append('comtypes')


setup(
    name='sword_pywifi',
    version='1.1',
    description='A Python package for try wifi password',
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="sword4869",
    url='https://github.com/sword4869/sword_pywifi',
    license='MIT License',
    install_requires=requires,
    entry_points={
        'console_scripts':[
            'sword_pywifi_gui = sword_pywifi.gui2:main',
            'sword_pywifi = sword_pywifi.cli:main',
        ]
    },
    package_data={'sword_pywifi': ['dictionary/*.txt', 'cache/*.txt'],}
)