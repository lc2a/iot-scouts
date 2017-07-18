from setuptools import setup

setup(
    name='ruuvitag-thingsboard',    
    version='0.56',                         
    scripts=['ruuvitag-thingsboard'],  
    install_requires=['paho-mqtt','ruuvitag_sensor']
)
