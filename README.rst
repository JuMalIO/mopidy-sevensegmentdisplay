****************************
Mopidy-SevenSegmentDisplay
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-SevenSegmentDisplay.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-SevenSegmentDisplay/
    :alt: Latest PyPI version

.. image:: https://travis-ci.org/JumalIO/mopidy-sevensegmentdisplay.svg?branch=master
    :target: https://travis-ci.org/JumalIO/mopidy-sevensegmentdisplay
    :alt: Travis-CI build status

.. image:: https://coveralls.io/repos/JumalIO/mopidy-sevensegmentdisplay/badge.svg?branch=master
    :target: https://coveralls.io/r/JumalIO/mopidy-sevensegmentdisplay
    :alt: Coveralls test coverage

A Mopidy extension for using it with seven segment display.

Installation
============

Install by running::

    pip install Mopidy-SevenSegmentDisplay


Configuration
=============

Optionally defaults can be configured in ``mopidy.conf`` config file (the default default values are shown below)::

    [sevensegmentdisplay]
    #default_song = local:track:Trance%201h/01-va_-_mainstation_trance_session_2008_day-ihq.mp3
    default_song = http://janus.shoutca.st:8788/stream

    #display_min_brightness = 2
    #display_max_brightness = 8
    display_min_brightness = 13
    display_max_brightness = 15
    display_off_time_from = 8
    display_off_time_to = 17


Usage
=============

Make sure that the `HTTP extension <http://docs.mopidy.com/en/latest/ext/http/>`_ is enabled. Then browse to the app on the Mopidy server (for instance, http://localhost:6680/sevensegmentdisplay/).


Changelog
=========

v0.1.0 (UNRELEASED)
----------------------------------------

- Initial release.
