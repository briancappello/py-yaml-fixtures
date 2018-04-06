from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Py YAML Fixtures',
    version='0.0.1',
    description='Load database fixtures from in Jinja-templated YAML files',
    long_description=long_description,
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
    packages=find_packages(include=['py_yaml_fixtures']),
    install_requires=[
        'faker>=0.8.7',
        'jinja2>=2.10',
        'python-dateutil>=2.6.1',
        'PyYAML>=3.12',
    ],
    python_requires='>=3.5',
    include_package_data=True,
    zip_safe=False,
)
