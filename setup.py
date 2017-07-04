import os
import sys
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

with open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'rb') as readme:
    README = readme.read()

class DjangoTest(TestCommand):

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import django
        from django.conf import settings
        from django.test.utils import get_runner
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
        django.setup()
        TestRunner = get_runner(settings)
        test_runner = TestRunner()
        failures = test_runner.run_tests(['tests'])
        sys.exit(bool(failures))

setup(
    name='django-simple-calendar',
    version='0.1',
    packages=find_packages(exclude=('tests','project')),
    include_package_data=True,
    license='MIT License',
    description='Django simple calendar app',
    long_description=README.decode(),
    url='https://github.com/naritotakizawa/django-simple-calendar',
    author='Narito Takizawa',
    author_email='toritoritorina@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    cmdclass = {'test': DjangoTest},
)
