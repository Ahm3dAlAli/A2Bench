from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="a2-bench",
    version="0.1.0",
    author="A2Bench Team",
    author_email="research@a2bench.org",
    description="A Quantitative Agent Evaluation Benchmark with Dual-Control Environments for Safety, Security, and Reliability",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/a2bench/a2-bench",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.18.0",
        "pyyaml>=6.0",
        "pydantic>=2.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "tqdm>=4.65.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "ruff>=0.0.270",
        ],
    },
    entry_points={
        "console_scripts": [
            "a2-bench=a2_bench.cli:main",
        ],
    },
)
