from ha_services.mqtt4homeassistant.components.sensor import Sensor
from ha_services.mqtt4homeassistant.device import MqttDevice
from ha_services.mqtt4homeassistant.utilities.string_utils import slugify


class UniqueIds:
    def __init__(self):
        self.uids = set()

    def get_unique_uid(self, name: str):
        base_uid = slugify(name.lower(), sep='_')
        for i in range(1, 100):
            uid = base_uid if i == 1 else f'{base_uid}_{i}'
            if uid not in self.uids:
                self.uids.add(uid)
                return uid
        raise ValueError(f'Could not generate unique UID for {name=} !')


class Obis2HaSensors:
    def __init__(self, definitions: dict, device: MqttDevice):
        self.obis_key2sensor = {}
        unique_ids = UniqueIds()
        for parameter in definitions['parameters']:
            sensor = Sensor(
                device=device,
                name=parameter['name'],
                uid=unique_ids.get_unique_uid(parameter['name']),
                device_class=parameter.get('class'),
                state_class=parameter.get('state_class'),
                unit_of_measurement=parameter.get('uom'),
                suggested_display_precision=parameter.get('suggested_display_precision'),
                min_value=parameter.get('min_value'),
                max_value=parameter.get('max_value'),
            )
            self.obis_key2sensor[parameter['obis_key']] = sensor

    def __getitem__(self, obis_key) -> Sensor:
        return self.obis_key2sensor[obis_key]
