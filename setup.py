from setuptools import setup, find_packages

setup(
    name="clearscan",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask>=3.0.0",
        "flask-httpauth>=4.8.0",
        "python-telegram-bot>=20.7",
        "pyyaml>=6.0.1",
        "python-nmap>=0.7.1",
        "SQLAlchemy>=2.0.25",
        "python-dotenv>=1.0.0",
        "schedule>=1.2.1",
        "requests>=2.31.0",
        "werkzeug>=3.0.1",
    ],
    python_requires=">=3.11",
) 