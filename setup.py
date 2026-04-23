from setuptools import find_packages, setup

setup(
    name='bluesales-python-sdk',
    version='2.0.0',
    packages=find_packages(),
    url='https://github.com/thehighestmath/bluesales-python-sdk',
    license='GPL-3.0',
    author='thehighestmath',
    author_email='kirill.lfybk.rh@gmail.com',
    description='Python SDK для BlueSales CRM API',
    python_requires='>=3.11',
    install_requires=[
        'requests>=2.25',
        'pytz>=2021.1',
    ],
    extras_require={
        'dev': [
            'pytest>=7',
            'ruff>=0.4',
            'mypy>=1.10',
            'types-requests',
        ],
    },
)
