"""
Setup script for Powerlytics Fivetran Connector
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="powerlytics-connector",
    version="1.0.0",
    author="Powerlytics Team",
    author_email="team@powerlytics.com",
    description="Fivetran custom connector for IoT energy data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/powerlytics/connector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "powerlytics-connector=connector:main",
        ],
    },
)
