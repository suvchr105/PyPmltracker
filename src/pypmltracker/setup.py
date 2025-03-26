from setuptools import setup, find_packages

setup(
    name="pypmltracker",
    version="0.1.2",
    author="Suvadip Chakraborty",
    author_email="suvadipchakraborty2006@gmail.com",
    description="A comprehensive ML experiment tracking library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/suvchr105/PyPmltracker",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy",
        "matplotlib",
        "flask",
        "psutil",
        "pillow",
        "requests",
    ],
    extras_require={
        "pytorch": ["torch"],
        "tensorflow": ["tensorflow"],
        "sklearn": ["scikit-learn"],
        "cloud": ["boto3"],
        "gpu": ["GPUtil"],
    },
)
