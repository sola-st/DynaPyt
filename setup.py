import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dynapyt",
    version="0.2.2",
    author="Aryaz Eghbali",
    author_email="aryaz.egh@gmail.com",
    description="Dynamic analysis framework for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sola-st/DynaPyt",
    project_urls={
        "Bug Tracker": "https://github.com/sola-st/DynaPyt/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src", "test": "test"},
    packages=setuptools.find_packages(where="src"),
    package_data={
        'dynapyt': ['utils/hierarchy.json'],
    },
    include_package_data=True,
    python_requires=">=3.6",
    setup_requires=[
        'libcst',
    ],
    install_requires=[
        'libcst',
    ],
)
