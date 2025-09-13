import logging
from pprint import pp

from cli_base.cli_tools.verbosity import setup_logging
from cli_base.tyro_commands import TyroVerbosityArgType
from rich import (
    get_console,  # noqa
    print,  # noqa
)

from pysmartmeter.cli_app import app
from pysmartmeter.user_settings import EnergyMeterDefinitions, UserSettings, get_user_settings


logger = logging.getLogger(__name__)


@app.command
def print_definition(verbosity: TyroVerbosityArgType):
    """
    Load definition file and print it.
    """
    setup_logging(verbosity=verbosity)
    user_settings: UserSettings = get_user_settings()
    energy_meter: EnergyMeterDefinitions = user_settings.energy_meter
    definitions: dict = energy_meter.get_definition()
    pp(definitions)


#
#
# TyroMaxPortArgType = Annotated[
#     int,
#     tyro.conf.arg(
#         # default=10,
#         help='Maximum USB port number',
#     ),
# ]
# TyroPortTemplateArgType = Annotated[
#     str,
#     tyro.conf.arg(
#         # default='/dev/ttyUSB{i}',
#         help='USB device path template'
#     ),
# ]
#
#
# def _get_energy_meter(verbosity: int) -> EnergyMeter:
#     user_settings: UserSettings = get_user_settings(verbosity)
#     energy_meter: EnergyMeter = user_settings.energy_meter
#     return energy_meter
#
#
# @app.command
# def probe_usb_ports(
#     verbosity: TyroVerbosityArgType, max_port: TyroMaxPortArgType, port_template: TyroPortTemplateArgType
# ):
#     """
#     Probe through the USB ports and print the values from definition
#     """
#     setup_logging(verbosity=verbosity)
#
#     energy_meter: EnergyMeter = _get_energy_meter(verbosity)
#     definitions = energy_meter.get_definitions()
#
#     for port_number in range(0, max_port):
#         port = port_template.format(i=port_number)
#         print(f'Probe port: {port}...')
#
#         energy_meter.port = port
#         try:
#             probe_one_port(energy_meter, definitions, verbosity)
#         except Exception as err:
#             print(f'ERROR: {err}')
#
#
# @app.command
# def print_definitions(verbosity: TyroVerbosityArgType):
#     """
#     Print RAW modbus register data
#     """
#     setup_logging(verbosity=verbosity)
#
#     energy_meter: EnergyMeter = _get_energy_meter(verbosity)
#     definitions = energy_meter.get_definitions()
#     pp(definitions)
#
#
# @app.command
# def print_values(verbosity: TyroVerbosityArgType):
#     """
#     Print all values from the definition in endless loop
#     """
#     setup_logging(verbosity=verbosity)
#
#     energy_meter: EnergyMeter = _get_energy_meter(verbosity)
#     definitions = energy_meter.get_definitions()
#
#     client = get_modbus_client(energy_meter, definitions, verbosity)
#
#     parameters = definitions['parameters']
#     if verbosity > 1:
#         pprint(parameters)
#
#     slave_id = energy_meter.slave_id
#     print(f'{slave_id=}')
#
#     while True:
#         print_parameter_values(client, parameters, slave_id, verbosity)
#
#
# @app.command
# def print_registers(verbosity: TyroVerbosityArgType):
#     """
#     Print RAW modbus register data
#     """
#     setup_logging(verbosity=verbosity)
#
#     energy_meter: EnergyMeter = _get_energy_meter(verbosity)
#     definitions = energy_meter.get_definitions()
#
#     client = get_modbus_client(energy_meter, definitions, verbosity)
#
#     parameters = definitions['parameters']
#     if verbosity > 1:
#         pprint(parameters)
#
#     slave_id = energy_meter.slave_id
#     print(f'{slave_id=}')
#
#     error_count = 0
#     address = 0
#     while error_count < 5:
#         print(f'[blue]Read register[/blue] dez: {address:02} hex: {address:04x} ->', end=' ')
#
#         response = client.read_holding_registers(address=address, count=1, slave=slave_id)
#         if isinstance(response, (ExceptionResponse, ModbusIOException)):
#             print('Error:', response)
#             error_count += 1
#         else:
#             assert isinstance(response, ReadHoldingRegistersResponse), f'{response=}'
#             for value in response.registers:
#                 print(f'[green]Result[/green]: dez:{value:05} hex:{value:08x}', end=' ')
#             print()
#
#         address += 1
