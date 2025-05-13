from setuptools import setup, find_packages

setup(
    # Surfpy package information
    name='surfpy',
    version='0.98.0',
    description='Wave and weather tools written in pure python',
    url='https://github.com/mpiannucci/surfpy',
    author='Matthew Iannucci',
    author_email='rhodysurf13@gmail.com',
    license='MIT',
    
    # Include both surfpy and ocean_data packages
    packages=['surfpy', 'ocean_data'],
    
    # Combined dependencies
    install_requires=[
        'requests', 
        'pytz', 
        'numpy',
        # Additional dependencies for ocean_data if needed
    ],
    
    # Optional dependencies
    extras_require={
        'pygrib': ['pygrib'],
        'jupyter': ['jupyter', 'pandas', 'matplotlib', 'plotly'],  # For data analysis
    },
    
    # Test configuration
    test_suite='nose.collector',
    tests_require=['nose'],
    setup_requires=['nose>=1.0'],
    
    # Additional metadata
    keywords='surfing, oceanography, buoy, weather, tide',
    python_requires='>=3.7',
    zip_safe=False
)
