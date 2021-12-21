import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'HISTORY.rst')).read()

requires = [
    'pyramid>=2.0',
    'skosprovider>=1.1.0'
]

tests_requires = [
    'pytest',
    'pytest-cov',
    'webtest'
]

testing_extras = tests_requires + []

setup(
    name='pyramid_skosprovider',
    version='1.1.0',
    license='MIT',
    description='Integration of skosprovider in pyramid',
    long_description=README + '\n\n' + CHANGES,
    long_description_content_type='text/x-rst',
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Pyramid',
    ],
    author='Koen Van Daele',
    author_email='koen_van_daele@telenet.be',
    url='https://github.com/OnroerendErfgoed/pyramid_skosprovider',
    keywords='pyramid skos skosprovider thesauri vocabularies',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=tests_requires,
    extras_require={
        'testing': testing_extras
    },
)
