class SerialMockEnds(StopIteration):
    pass


class SerialMock:
    def __init__(self, lines):
        self.lines = iter(lines)

    def __call__(self):
        return self

    def readline(self):
        try:
            return next(self.lines)
        except StopIteration:
            raise SerialMockEnds


class MqttClientMock:
    def __init__(self):
        self.init = []
        self.enabled_logger = []
        self.credentials = []
        self.connects = []
        self.loop_started = False
        self.published = []

    def __call__(self, *args, **kwargs):
        self.init.append([args, kwargs])
        return self

    def enable_logger(self, logger):
        self.enabled_logger.append(logger)

    def username_pw_set(self, user_name, password):
        self.credentials.append(dict(user_name=user_name, password=password))

    def connect(self, host, port):
        self.connects.append(dict(host=host, port=port))

    def loop_start(self):
        self.loop_started = True

    def is_connected(self):
        if self.connects and self.loop_started:
            return True
        return False

    def publish(self, **kwargs):
        self.published.append(kwargs)

    def assert_state(self, test_class, *, init, enabled_logger, credentials, connects, loop_started):
        test_class.assertEqual(self.init, init)
        test_class.assertEqual(self.enabled_logger, enabled_logger)
        test_class.assertEqual(self.credentials, credentials)
        test_class.assertEqual(self.connects, connects)
        test_class.assertEqual(self.loop_started, loop_started)

    def loop_stop(self):
        pass

    def disconnect(self):
        pass


class MqttPublisherMock:
    mqtt_payloads = []

    def publish(self, *, mqtt_payload):
        self.mqtt_payloads.append(mqtt_payload)


class SocketMock:
    def __init__(self):
        self.getaddrinfos = []

    def gethostname(self):
        return 'mocked get hostname'

    def setdefaulttimeout(self, timeout):
        pass

    def getaddrinfo(self, host, port):
        self.getaddrinfos.append((host, port))
        return True
