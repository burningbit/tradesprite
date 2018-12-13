# coding=utf-8


class TradespriteAPIException(Exception):
    def __init__(self, response):
        self.code = 0
        try:
            parsed_json = response.json()
        except ValueError:
            self.message = 'Invalid JSON error message from Tradesprite: {}'.format(response.text)
        else:
            self.status = parsed_json.get('status')
            self.message = parsed_json.get('message')
        self.status_code = response.status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return 'APIError(status=%s): %s' % (self.status, self.message)


class TradespriteAuthException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'TradespriteAuthException: %s' % self.message


class TradespriteInvalidRequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'TradespriteInvalidRequestException: %s' % self.message


class TradespriteRequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'TradespriteRequestException: %s' % self.message
