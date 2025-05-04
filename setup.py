from setuptools import setup, find_packages

setup(
    name="linux-task-manager",
    version="0.2.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    
    # Dependencies
    install_requires=[
        "psutil",
        "PyGObject",
    ],
    
    # Metadata
    author="Mustafa Balaban",
    author_email="mustafabalaban46@gmail.com",
    description="A system task manager for Linux",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mbalaban1776/Linux-Task-Manager",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: GTK",
    ],
    
    # Entry points
    entry_points={
        "console_scripts": [
            "linux-task-manager=main:main",
        ],
    },
)