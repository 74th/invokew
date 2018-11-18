import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="invokew",
    version="0.1.0",
    author="74th",
    author_email="site@j74th.com",
    description="type hints for invoke",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/74th/invokew",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ),
)
