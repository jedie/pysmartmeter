import logging

from cli_base.cli_tools.verbosity import setup_logging
from cli_base.tyro_commands import TyroVerbosityArgType
from rich import get_console  # noqa
from rich import print  # noqa; noqa

from pysmartmeter.cli_app import app
from pysmartmeter.mqtt_handler import MqttHandler
from pysmartmeter.mqtt_publish import publish_forever
from pysmartmeter.user_settings import UserSettings, get_user_settings


logger = logging.getLogger(__name__)


@app.command
def publish_loop(verbosity: TyroVerbosityArgType):
    """
    Publish all values via MQTT to Home Assistant in a endless loop.
    """
    setup_logging(verbosity=verbosity)
    user_settings: UserSettings = get_user_settings()
    handler = MqttHandler(user_settings=user_settings)
    publish_forever()
