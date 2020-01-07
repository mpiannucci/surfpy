from setuptools import setup

setup(name='surfpy',
      version='0.2.0',
      description='Wave and weather tools written in pure python',
      url='https://github.com/mpiannucci/surfpy',
      author='Matthew Iannucci',
      author_email='rhodysurf13@gmail.com',
      license='MIT',
      packages=['surfpy'],
      install_requires=['grippy', 'requests', 'pytz'],
      dependency_links=['https://github.com/mpiannucci/grippy/tarball/master#egg=grippy-0.1.0'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)