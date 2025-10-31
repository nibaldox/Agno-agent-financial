"""
Setup configuration for Agno Trading System
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text().splitlines()
    # Filter out comments and empty lines
    requirements = [r.strip() for r in requirements if r.strip() and not r.startswith("#")]

setup(
    name="agno-trading-system",
    version="2.1.0",
    author="Romamo",
    author_email="",  # Agregar tu email
    description="Sistema avanzado de trading con agentes AI y analytics profesionales",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Romamo/agno-trading-system",  # Actualizar con tu repo
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agno-report=examples.generate_report:main",
            "agno-agents=examples.run_agents:main",
            "agno-workflow=examples.complete_workflow:main",
        ],
    },
    package_data={
        "agno_trading": [
            "agents/configs/*.yaml",
            "core/templates/*.html",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "trading",
        "ai",
        "agents",
        "agno",
        "finance",
        "analytics",
        "portfolio",
        "investment",
        "machine-learning",
    ],
    project_urls={
        "Bug Reports": "https://github.com/Romamo/agno-trading-system/issues",
        "Source": "https://github.com/Romamo/agno-trading-system",
        "Documentation": "https://github.com/Romamo/agno-trading-system/tree/main/docs",
    },
)
