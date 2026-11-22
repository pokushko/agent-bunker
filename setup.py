# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="agent-bunker",
    version="1.0.0",
    description="Production-Grade Chaos Engineering & 24/7 Resilience Harness for Autonomous AI Agents",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Roman Pokushko",
    author_email="roman.pokushko@mail.ru",
    url="https://github.com/pokushko/agent-bunker",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "psutil>=5.9.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0"]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Testing",
    ],
    keywords="ai-agents, llm, chaos-engineering, reliability, multi-agent, resilience, oom-guard, wal",
)
