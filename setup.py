from setuptools import setup, find_packages

setup(
    name='kaal_engine',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'skyfield',
        'astropy',
        'geographiclib',
        'pyerfa'
    ],
    include_package_data=True,
    package_data={
        'kaal_engine': ['data/*.bsp'],
    },
    entry_points={
        'console_scripts': [
            'kaal = kaal_engine.cli:main',
        ],
    },
) 