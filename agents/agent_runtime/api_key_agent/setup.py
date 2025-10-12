from setuptools import setup, find_packages

setup(
    name="api-key-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "cryptography",
        "pytest",
        "python-dotenv"
    ],
    entry_points={
        "console_scripts": [
            "apikey-check=cli:run_cli"
        ]
    },
    author="Your Name",
    description="Universal API key validator and agent runtime",
    keywords=["API", "Key", "Validator", "Agent"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
