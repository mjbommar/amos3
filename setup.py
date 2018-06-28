from setuptools import setup, find_packages

setup(
    name='amos3',
    version='0.1.0',
    packages=find_packages(exclude=['*tests*']),
    package_dir={'': '.'},
    install_requires=[
        'coveralls==1.3.0',
        'lxml',
        'nose',
        'numpy',
        'pytest-cov',
        'python-dateutil',
        'pytest-pylint',
        'requests',
    ],
    url='https://github.com/mjbommar/amos3',
    license='MIT License',
    author='Michael J Bommarito II',
    author_email='michael.bommarito@gmail.com',
    description='Python 3 client for Archive of Many Outdoor Scenes (AMOS)',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='amos outdoor scene computer vision dataset',

)
