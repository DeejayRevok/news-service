from aiohttp import ClientSession
from aiohttp.web_exceptions import HTTPUnauthorized


class UaaService:
    URL_BASE = '{protocol}://{host}:{port}/{path}'
    PATHS = {'validate_token': 'v1/api/auth/token'}

    def __init__(self, protocol, host, port):
        self._protocol = protocol
        self._host = host
        self._port = int(port)

    async def validate_token(self, token):
        async with ClientSession() as client:
            fetch_user_url = self.URL_BASE.format(protocol=self._protocol, host=self._host, port=self._port,
                                                  path=self.PATHS['validate_token'])
            try:
                async with client.post(fetch_user_url, data=dict(token=token)) as response:
                    if response.status == 200:
                        response_json = await response.json()
                    elif response.status == 500:
                        raise HTTPUnauthorized(reason='Wrong authorization token')
                    else:
                        raise ConnectionError(f'Error calling uaa service')
            except Exception as ex:
                raise ConnectionError(f'Error calling uaa service {str(ex)}')

        if 'id' in response_json:
            return response_json
        else:
            raise HTTPUnauthorized(reason='Wrong authorization token')
