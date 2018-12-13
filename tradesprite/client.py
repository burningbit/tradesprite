import requests

from tradesprite.exceptions import TradespriteAPIException, TradespriteAuthException, TradespriteRequestException


class Client(object):
    EXCHANGE_HOST = 'https://alpha.tradesprite.com/api'
    API_VERSION = 'v1'
    MAX_RETRY_COUNT = 3

    def __init__(self, client_id, password, request_params=None):
        self.CLIENT_ID = client_id
        self.PASSWORD = password
        self._request_params = request_params
        self._init_session()
        self._refresh_auth_token()

    def _refresh_auth_token(self):
        if not self.session:
            self.session = self._init_session()

        session = self.session
        login_response = self.login()
        auth_token = login_response.get('auth_token', '')
        session.headers.update({'X-Authorization-Token': auth_token})

    def _init_session(self):
        self.session = requests.session()
        return self.session

    def _create_api_uri(self, path, version=API_VERSION):
        return self.EXCHANGE_HOST + '/' + version + '/' + path

    def _request_api(self, method, path, version=API_VERSION, **kwargs):
        uri = self._create_api_uri(path, version)
        return self._request(method, uri, **kwargs)

    def _request(self, method, uri, **kwargs):
        kwargs['timeout'] = 30  # default request timeout

        data = kwargs.get('data', None)

        if data and method == 'get':
            kwargs['params'] = kwargs['data']

        response = getattr(self.session, method)(uri, **kwargs)

        retry_count = 0
        while retry_count < self.MAX_RETRY_COUNT:
            response, retry_count = self._handle_response(response, retry_count)

        return response

    def _handle_response(self, response, retry_count=0):
        if response.status_code == 401:
            if retry_count + 1 == self.MAX_RETRY_COUNT:
                raise TradespriteAuthException("Authentication failed, please make sure you have correct permissions")

            # Refresh access token and retry
            self._refresh_auth_token()
            return None, (retry_count + 1)

        if not str(response.status_code).startswith('2'):
            raise TradespriteAPIException(response)

        try:
            resp = response.json()
            status = resp.get('status', 'error')
            if not status == 'success':
                raise TradespriteRequestException("Error in API %s" % response.text)
            return resp.get('data', {}), self.MAX_RETRY_COUNT
        except ValueError:
            raise TradespriteRequestException('Invalid Response: %s' % response.text)

    def _get(self, path, version=API_VERSION, **kwargs):
        return self._request_api('get', path, version, **kwargs)

    def _post(self, path, version=API_VERSION, **kwargs):
        return self._request_api('post', path, version, **kwargs)

    def _put(self, path, version=API_VERSION, **kwargs):
        return self._request_api('put', path, version, **kwargs)

    def _delete(self, path, version=API_VERSION, **kwargs):
        return self._request_api('delete', path, version, **kwargs)

    # Exchange endpoints #

    # User profile
    def login(self):
        login_payload = {
            'login_id': self.CLIENT_ID,
            'password': self.PASSWORD
        }

        return self._post('login', data=login_payload)

    def get_user_details(self):
        return self._get('user_details', self.API_VERSION, data=dict(client_id=self.CLIENT_ID))

    # Trades
    def get_trades(self, **params):
        """
        :param params:
            - start_time | Optional | Unix Epoch Nano Seconds Intger
            - end_time   | Optional | Unix Epoch Nano Seconds Intger
        :return: Trades
        """
        params['client_id'] = self.CLIENT_ID
        return self._get('trades', self.API_VERSION, data=params)

    # Orders
    def create_order(self, **params):
        params['client_id'] = self.CLIENT_ID
        return self._post('orders', self.API_VERSION, data=params)

    def modify_order(self, **params):
        params['client_id'] = self.CLIENT_ID
        return self._put('orders', self.API_VERSION, data=params)

    def cancel_order(self, order_id):
        path = 'orders/{order_id}'.format(order_id=order_id)
        return self._delete(path, self.API_VERSION, data=dict(client_id=self.CLIENT_ID))