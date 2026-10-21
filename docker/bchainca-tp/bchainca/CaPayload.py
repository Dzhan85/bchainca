import dateutil.parser

from sawtooth_sdk.processor.exceptions import InvalidTransaction


class CaPayload(object):
    """Payload format: "<action>|<ISO-8601 UTC date>|<value>".

    For 'create' and 'init' the value is a PEM document (CSR or encrypted
    CA key); for the other actions it is a decimal certificate serial.
    """

    def __init__(self, payload):
        try:
            action, date, value = payload.decode('utf-8').split("|", 2)
        except ValueError:  # also covers UnicodeDecodeError
            raise InvalidTransaction('Malformed payload')

        if action not in ('create', 'init', 'get', 'revoke', 'status'):
            raise InvalidTransaction('Invalid action: {}'.format(action))

        self._value = None
        self._serial = None
        if action in ('create', 'init'):
            self._value = value.encode('utf-8')
        elif value.isdigit():
            self._serial = value
        else:
            raise InvalidTransaction('Invalid serial number: {}'.format(value))

        try:
            self._date = dateutil.parser.parse(date)
        except (ValueError, OverflowError):
            raise InvalidTransaction('Invalid date: {}'.format(date))

        self._action = action

    @property
    def action(self):
        return self._action

    @property
    def value(self):
        return self._value

    @property
    def date(self):
        return self._date

    @property
    def serial(self):
        return self._serial
