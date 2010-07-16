from distutils.core import setup

setup(name='nmea',
      version='0.2',
      description='Python NMEA Toolkit',
      long_description="The NMEA toolkit can be used as a standalone library for accessing an NMEA device, it is currently readonly and does not support two way communication with a NMEA device. The current implementation only handles nmea sentences that relate to GPS.",
      author='Tim Savage',
      author_email='tim+python-gpsd@poweredbypenguins.org',
      url='http://code.google.com/p/python-gpsd/',
      license='GNU General Public License version 3',
      platforms='OS Independent',
      packages=['nmea'],
      package_dir={'nmea': ''},
      scripts=[
        'nmea_record', 'nmea_playback'
      ],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)'
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries'
      ]
)
