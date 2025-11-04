"""Setup configuration for ZETA CLI."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="zeta-cli",
    version="1.0.6",
    description="ZETA - Zero-Latency Editing Terminal Agent: A friendly local AI terminal agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sukin Shetty",
    author_email="sukin.shetty8@gmail.com",
    url="https://github.com/SukinShetty/Zeta-CLI",
    py_modules=["zeta"],
    license="MIT",
    install_requires=[
        "click>=8.0.0",
        "langchain>=1.0.0",
        "langgraph>=1.0.0",
        "rich>=14.0.0",
        # Ollama is default, but users can use cloud APIs instead
        "langchain-ollama>=1.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "zeta=zeta:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="cli ai terminal agent ollama langchain",
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
            "pytest-cov>=4.0.0",
            "pytest-timeout>=2.1.0",
        ],
        "openai": ["langchain-openai>=1.0.0"],
        "anthropic": ["langchain-anthropic>=1.0.0"],
        "google": ["langchain-google-genai>=1.0.0"],
        "all": [
            "langchain-openai>=1.0.0",
            "langchain-anthropic>=1.0.0",
            "langchain-google-genai>=1.0.0",
        ],
    },
    test_suite="tests",
)

