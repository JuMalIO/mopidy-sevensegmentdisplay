****************************
Mopidy-SevenSegmentDisplay
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-SevenSegmentDisplay.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-SevenSegmentDisplay/
    :alt: Latest PyPI version

.. image:: https://travis-ci.org/JuMalIO/mopidy-sevensegmentdisplay.svg?branch=master
    :target: https://travis-ci.org/JuMalIO/mopidy-sevensegmentdisplay
    :alt: Travis-CI build status

.. image:: https://coveralls.io/repos/JuMalIO/mopidy-sevensegmentdisplay/badge.svg?branch=master
    :target: https://coveralls.io/r/JuMalIO/mopidy-sevensegmentdisplay
    :alt: Coveralls test coverage

A Mopidy extension for using it with seven segment display.

.. figure:: https://bit.ly/2QRAsZm
|
.. figure:: https://s2.gifyu.com/images/18af69fdf5a34049f.gif
|
.. figure:: https://s2.gifyu.com/images/24fc76ce4a5b78ef6.gif

Installation
============

Install by running::

    pip install Mopidy-SevenSegmentDisplay


Configuration
=============

Optionally defaults can be configured in ``mopidy.conf`` config file (the default default values are shown below)::

    [sevensegmentdisplay]

    buttons_enabled = false
    light_sensor_enabled = true
    relay_enabled = false
    ir_receiver_enabled = true

    default_tracks = http://janus.shoutca.st:8788/stream
    
    default_volume = 20
    default_preset = flat

    light_sensor_volume = 5
    light_sensor_preset = nobass
    light_sensor_time_from = 22
    light_sensor_time_to = 4

    display_min_brightness = 13
    display_max_brightness = 15
    display_off_time_from = 8
    display_off_time_to = 17


Usage
=============

Make sure that the `HTTP extension <http://docs.mopidy.com/en/latest/ext/http/>`_ is enabled. Then browse to the app on the Mopidy server (for instance, http://localhost/sevensegmentdisplay/).


Changelog
=========

v0.3.0
----------------------------------------

- Timers added to webpage
- Possibility to disable features in config
- Music presets moved from sh to python
- Menu animations changed
- Light sensor added
- Reboot/halt menu added
- Refactoring
- Minor adjustments

v0.2.1
----------------------------------------

- Refactoring release.

v0.2.0
----------------------------------------

- Initial release.

v0.1.0 (UNRELEASED)
----------------------------------------

- Initial release.
