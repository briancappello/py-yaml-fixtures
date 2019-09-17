from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Py-YAML-Fixtures',
    version='0.5.0',
    description='Load Django and SQLAlchemy database fixtures '
                'from Jinja-templated YAML files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/briancappello/py-yaml-fixtures',
    author='Brian Cappello',
    license='MIT',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=[
        'faker>=1.0.7',
        'jinja2>=2.10.1',
        'networkx>=2.3',
        'python-dateutil>=2.8.0',
        'PyYAML>=5.1',
    ],
    extras_require={
        'dev': [
            'django>=2.1',
            'flask>=1.0',
            'pytest',
            'sqlalchemy>=1.0',
        ],
        'django': [
            'django>=2.0',
        ],
        'docs': [
            'django>=2.1',
            'flask>=1.0',
            'm2r',
            'sphinx',
            'sphinx-autobuild',
            'sphinx-rtd-theme',
            'sqlalchemy>=1.0',
        ],
        'flask-sqlalchemy': [
            'click>=6.7',
            'flask>=1.0',
            'flask-sqlalchemy>=2.2',
        ],
        'flask-unchained': [
            'flask-migrate>=2.2.1',
            'flask-unchained>=0.7.9',
            'flask-sqlalchemy-unchained>=0.7.3',
            'sqlalchemy-unchained>=0.7.6',
        ],
        'sqlalchemy': [
            'sqlalchemy>=1.0',
        ],
    },
    python_requires='>=3.5',
    include_package_data=True,
    zip_safe=False,
)
