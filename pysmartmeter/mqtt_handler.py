import logging

from ha_services.mqtt4homeassistant.components.sensor import Sensor
from ha_services.mqtt4homeassistant.device import MainMqttDevice, MqttDevice
from ha_services.mqtt4homeassistant.mqtt import get_connected_client

from pysmartmeter.user_settings import UserSettings


logger = logging.getLogger(__name__)


class MqttHandler:
    def __init__(self, user_settings: UserSettings):
        self.user_settings = user_settings
        self.device_name = user_settings.device_name

        self.mqtt_client = get_connected_client(settings=user_settings.mqtt, verbosity=verbosity)
        self.mqtt_client.loop_start()

        self.main_device = None

    def init_device(self, *, parsed_data: TC66PollData):
        self.main_device = MainMqttDevice(
            name='TC66C 2 MQTT',
            uid=str(parsed_data.serial),
            manufacturer='tc66c2mqtt',
            sw_version=tc66c2mqtt.__version__,
            config_throttle_sec=self.user_settings.mqtt.publish_config_throttle_seconds,
        )
        self.mqtt_device = MqttDevice(
            main_device=self.main_device,
            name=self.device_name,
            uid=parsed_data.product_name,
            manufacturer='RDTech',
            sw_version=parsed_data.version,
            config_throttle_sec=self.user_settings.mqtt.publish_config_throttle_seconds,
        )
