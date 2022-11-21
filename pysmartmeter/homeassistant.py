"""
    https://github.com/home-assistant/core/blob/dev/homeassistant/components/mqtt/discovery.py
"""
from bx_py_utils.humanize.time import human_timedelta

from pysmartmeter import ha_const
from pysmartmeter.data_classes import HomeassistantValue, ObisValue
from pysmartmeter.obis_map import OBIS_OPERATION_DURATION_KEY
from pysmartmeter.utilities.string_utils import slugify


HA_COMPONENT = 'sensor'


def value_key(raw_key):
    return f'value_{slugify(raw_key)}'


def get_value_by_key(values, key: str):
    for value in values:
        if value.key == key:
            return value
    raise KeyError(key)


def data2config(ha_values: list[HomeassistantValue]) -> list[dict]:
    identifier_value = get_value_by_key(values=ha_values, key='identifier')
    identifier_raw = identifier_value.obis_value.value
    assert identifier_raw
    identifier_slug = slugify(identifier_raw)

    state_topic = f'{ha_const.DEFAULT_PREFIX}/{HA_COMPONENT}/{identifier_slug}/state'

    identifiers = [ha_value.unique_id for ha_value in ha_values]

    configs = []
    for ha_value in ha_values:
        config_topic = f'{ha_const.DEFAULT_PREFIX}/{HA_COMPONENT}/{ha_value.unique_id}/config'
        value_template = '{{ value_json.%(value_key)s }}' % dict(value_key=ha_value.value_key)

        configs.append(
            dict(
                topic=config_topic,
                data={
                    ha_const.CONF_DEVICE_CLASS: 'energy',
                    ha_const.CONF_DEVICE: {
                        'name': identifier_raw,
                        'identifiers': identifiers,
                    },
                    'name': ha_value.obis_value.name,
                    'unique_id': ha_value.unique_id,
                    'state_class': 'measurement',
                    ha_const.CONF_STATE_TOPIC: state_topic,
                    'unit_of_measurement': ha_value.obis_value.unit,
                    'value_template': value_template,
                },
            )
        )

    return configs


def data2state(ha_values: list[HomeassistantValue]) -> dict:
    identifier_value = get_value_by_key(values=ha_values, key='identifier')
    identifier_raw = identifier_value.obis_value.value
    assert identifier_raw
    identifier_slug = slugify(identifier_raw)

    payload = {ha_value.value_key: ha_value.obis_value.value for ha_value in ha_values}
    result = dict(
        topic=f'{ha_const.DEFAULT_PREFIX}/{HA_COMPONENT}/{identifier_slug}/state',
        data=payload,
    )

    return result


def ha_convert_obis_values(*, obis_values: list[ObisValue]) -> list[HomeassistantValue]:
    identifier_value = get_value_by_key(values=obis_values, key='identifier')
    identifier_raw = identifier_value.value
    assert identifier_raw
    identifier_slug = slugify(identifier_raw).lower()

    ha_values = []
    for value in obis_values:
        unique_id = f'{identifier_slug}_{value.key_slug}'
        ha_values.append(
            HomeassistantValue(
                unique_id=unique_id,
                value_key=f'value_{value.key_slug}',
                obis_value=value,
            )
        )

    # Get the RAW operation time in seconds:
    try:
        operation_duration = get_value_by_key(values=obis_values, key=OBIS_OPERATION_DURATION_KEY)
    except KeyError:
        pass
    else:
        # Add a human-readable operation time entry:
        op_sec = operation_duration.value
        obis_value: ObisValue = operation_duration.copy()
        op_str = human_timedelta(op_sec)
        value, unit = op_str.split('\xa0')
        obis_value.value = float(value)  # type: ignore[arg-type]
        obis_value.unit = unit
        ha_values.append(
            HomeassistantValue(
                unique_id=f'{identifier_slug}_human_op_time',
                value_key='value_human_op_time',
                obis_value=obis_value,
            )
        )

    return ha_values