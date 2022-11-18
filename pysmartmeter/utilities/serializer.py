import dataclasses


def serialize_values(data):
    if isinstance(data, list):
        return [serialize_values(entry) for entry in data]
    elif isinstance(data, dict):
        return {serialize_values(key): serialize_values(value) for key, value in data.items()}
    elif isinstance(data, (str, int, float)):
        return data
    elif dataclasses.is_dataclass(data):
        return dataclasses.asdict(data)

    raise NotImplementedError(f'Unsupported: {data!r} (type: {type(data).__name__})')
