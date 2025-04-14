from setuptools import setup, find_packages

setup(
    name="habitx",  # the name used on PyPI and pip
    version="0.1.0",
    description="A CLI-based habit tracker to build and track healthy habits",
    author="Dev Mad",
    author_email="maddev@example.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'habit_tracker': ['../demo.json'],  # Adjust path as needed
    },
    install_requires=[
        "fire",
        "pyfiglet",
        "pytz",
        "tabulate",
        "rich",
        "peewee",
        "pytest",
        "python-dateutil"
    ],
    entry_points={
        "console_scripts": [
            "habitx=habit_tracker.main:main",
        ]
    },
    python_requires=">=3.8",
)
