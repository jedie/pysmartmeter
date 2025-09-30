from unittest import TestCase

from ha_services.ha_data.validators import ValidationError, validate_sensor

from pysmartmeter.user_settings import DEFINITION_FILES_PATH, parse_definition


class DefinitionTestCase(TestCase):
    def test_validate_all_definitions(self):
        with self.assertLogs(logger=None):
            entries = DEFINITION_FILES_PATH.glob('*.toml')
            for entry in entries:
                definitions = parse_definition(name=entry.stem)
                for sensor_definition in definitions['parameters']:
                    try:
                        validate_sensor(
                            device_class=sensor_definition.get('class'),
                            state_class=sensor_definition.get('state_class'),
                            unit_of_measurement=sensor_definition.get('uom'),
                        )
                    except ValidationError as err:
                        self.fail(f'ValidationError for "{sensor_definition["name"]}":\n{err}')
