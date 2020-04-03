"""
Setup module for the event service library
"""
import os
from os.path import dirname
from typing import List

import setuptools


def get_requirements() -> List[str]:
    """
    Parse the requirements of the package into a list of requirements

    Returns: list of package requirements

    """
    with open(os.path.join(dirname(__file__), 'requirements.txt')) as requirements:
        return requirements.readlines()


setuptools.setup(
    name='event_service_lib',
    version="0.0.1",
    author="DeejayRevok",
    author_email="seryi_one@hotmail.com",
    description="Event service microservices library",
    url="https://github.com/DeejayRevok/event-service/tree/develop/event_service_lib",
    packages=['event_service_lib', 'event_service_lib.tests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
    install_requires=get_requirements(),
    python_requires='>=3.7',
    )
