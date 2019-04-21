from __future__ import unicode_literals

import os
from http import factory_decorator
from actor import Frontend
from mopidy import config, ext

__version__ = '0.3.0'


class Extension(ext.Extension):
    dist_name = 'Mopidy-SevenSegmentDisplay'
    ext_name = 'sevensegmentdisplay'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['buttons_enabled'] = config.Boolean()
        schema['light_sensor_enabled'] = config.Boolean()
        schema['relay_enabled'] = config.Boolean()
        schema['ir_receiver_enabled'] = config.Boolean()
        schema['default_tracks'] = config.String()
        schema['default_volume'] = config.Integer()
        schema['default_preset'] = config.String()
        schema['light_sensor_volume'] = config.Integer()
        schema['light_sensor_preset'] = config.String()
        schema['light_sensor_time_from'] = config.Integer()
        schema['light_sensor_time_to'] = config.Integer()
        schema['alert_files'] = config.String()
        schema['display_min_brightness'] = config.Integer()
        schema['display_max_brightness'] = config.Integer()
        schema['display_off_time_from'] = config.Integer()
        schema['display_off_time_to'] = config.Integer()
        return schema

    def setup(self, registry):
        registry.add('frontend', Frontend)
        registry.add('http:app', {
            'name': self.ext_name,
            'factory': factory_decorator(Frontend.worker),
        })
