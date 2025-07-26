from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="show-my-lyrics",
    version="0.6.0",
    author="Mert Ali İlter",
    author_email="iltermertali441@gmail.com",
    description="A beautiful desktop application that displays real-time synchronized lyrics for your Spotify music",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ritiam/show-my-lyrics",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Desktop Environment",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "show-my-lyrics=App:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["images/*.svg", "*.json"],
    },
)