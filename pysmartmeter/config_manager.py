import os
class ConfigManager(object):
    _is_initialized = False
    _SML_BINARY_TEST_MESSAGE:bytearray = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ConfigManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if self._is_initialized:
            return
        self._is_initialized = True
        self._MODULE_BINPARSER_VERBOSE = self._get_bool_environment ("MODULE_BINPARSER_VERBOSE")
        self._MODULE_OBIS_VERBOSE = self._get_bool_environment ("MODULE_OBIS_VERBOSE")
        self._ADD_TIMESTAMP = self._get_bool_environment("ADD_TIMESTAMP")
        self._BINARY_MODE = self._get_bool_environment("BINARY_MODE")

        self._EXTERNAL_SERVER_ID = os.environ.get("EXTERNAL_SERVER_ID", None)

        if os.environ.get("SML_BINARY_TEST_MESSAGE", None) is not None:
            res = os.environ.get("SML_BINARY_TEST_MESSAGE", None).replace(' ', '')
            if (len(res) < 10):
                self._SML_BINARY_TEST_MESSAGE = None
            else:
                self._SML_BINARY_TEST_MESSAGE = bytearray.fromhex(res)

        return

    def _get_bool_environment (self, env_var) -> bool:
        return  (True if os.environ.get(env_var, "False").upper() == "TRUE" else False)

    @property
    def MODULE_BINPARSER_VERBOSE (self) -> bool:
        return self._MODULE_BINPARSER_VERBOSE

    @property
    def MODULE_OBIS_VERBOSE (self) -> bool:
        return self._MODULE_OBIS_VERBOSE

    @property
    def BINARY_MODE (self) -> bool:
        return self._BINARY_MODE

    @property
    def ADD_TIMESTAMP (self) -> bool:
        return self._ADD_TIMESTAMP

    @property
    def EXTERNAL_SERVER_ID (self) -> str:
        return self._EXTERNAL_SERVER_ID

    @property
    def SML_BINARY_TEST_MESSAGE (self) -> bytearray:
        return self._SML_BINARY_TEST_MESSAGE


    @property
    def dummy (self) -> int:
        return (self._dummy)

    @dummy.setter
    def dummy(self, a):
        self._dummy = a

#singleton = ConfigManager()
#new_singleton = ConfigManager()

#print(singleton is new_singleton)

#singleton.singl_variable = "Singleton Variable"
#print(new_singleton.singl_variable)
