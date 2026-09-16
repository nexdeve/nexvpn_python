from setuptools import setup, find_packages

setup(
    name="nexvpn",
    version="1.0.0",
    description="Easy Python OpenVPN wrapper — VPN connection management for desktop & server",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="NexTech",
    url="https://github.com/nexdeve/nexvpn_python",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Internet",
    ],
)
