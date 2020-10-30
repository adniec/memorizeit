from setuptools import setup

from memorizeit import __version__

with open('README.md') as readme:
    long_description = readme.read()

with open('requirements.txt') as required:
    requirements = required.read()

setup(
    name='memorizeit',
    version=__version__,
    author='Adrian Niec',
    author_email='ethru@protonmail.com',
    description=' Game for memory and focus training.',
    long_description=long_description,
    url='https://github.com/ethru/memorizeit',
    license='MIT',
    platforms=['any'],
    install_requires=requirements,
    python_requires='>=3.7',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Topic :: Games/Entertainment',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.7',
                 ],
    packages=['memorizeit'],
    include_package_data=True,
    entry_points={
        'gui_scripts': [
            'memorizeit = memorizeit.__main__:main'
        ],
    },
)
