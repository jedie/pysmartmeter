import logging

from ha_services.mqtt4homeassistant.components.sensor import Sensor
from ha_services.mqtt4homeassistant.data_classes import MqttSettings
from ha_services.mqtt4homeassistant.device import MainMqttDevice, MqttDevice
from ha_services.mqtt4homeassistant.mqtt import get_connected_client

import pysmartmeter
from pysmartmeter.data_classes import ObisValue
from pysmartmeter.obis2ha_sensors import Obis2HaSensors
from pysmartmeter.user_settings import Hichi, UserSettings


logger = logging.getLogger(__name__)


class HichiMqttHandler:
    def __init__(self, user_settings: UserSettings, verbosity: int):
        self.user_settings = user_settings
        hichi: Hichi = self.user_settings.hichi

        mqtt_settings: MqttSettings = user_settings.mqtt

        self.mqtt_client = get_connected_client(settings=mqtt_settings, verbosity=verbosity)
        # self.mqtt_client.loop_start()

        self.main_device = MainMqttDevice(
            name='pysmartmeter',
            uid=mqtt_settings.main_uid,
            manufacturer='pysmartmeter',
            sw_version=pysmartmeter.__version__,
            config_throttle_sec=mqtt_settings.publish_config_throttle_seconds,
        )
        self.mqtt_device = MqttDevice(
            main_device=self.main_device,
            name=hichi.verbose_name,
            uid=hichi.name,
            manufacturer=hichi.manufacturer,
            sw_version=None,
            config_throttle_sec=mqtt_settings.publish_config_throttle_seconds,
        )

        #################################################################################

        definitions: dict = hichi.get_definitions()
        # definitions = {'parameters': [{'register': 28,
        #                              'reg_count': 2,
        #                              'name': 'Energy Counter Total',
        #                              'class': 'energy',
        #                              'state_class': 'total',
        #                              'uom': 'kWh',
        #                              'scale': 0.01},
        #                             {...

        self.obis2ha_sensors = Obis2HaSensors(
            definitions=definitions,
            device=self.mqtt_device,
        )

    def __call__(self, obis_values: list[ObisValue]):
        logger.debug('Process %i obis values', len(obis_values))

        self.main_device.poll_and_publish(self.mqtt_client)

        for obis_value in obis_values:
            obis_key = obis_value.key

            try:
                sensor: Sensor = self.obis2ha_sensors[obis_key]
            except KeyError:
                logger.exception('No sensor for obis key %r', obis_key)
                continue

            sensor.set_state(state=obis_value.value)
            sensor.publish(self.mqtt_client)
