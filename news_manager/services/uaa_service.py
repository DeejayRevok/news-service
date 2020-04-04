"""
Module which implements the service used to interact with the UAA service
"""
from aiohttp import ClientSession
from aiohttp.web_exceptions import HTTPUnauthorized


class UaaService:
    """
    Class used to interact with the UAA service
    """
    URL_BASE = '{protocol}://{host}:{port}/{path}'
    PATHS = {'validate_token': 'v1/api/auth/token'}

    def __init__(self, protocol: str, host: str, port: str):
        """
        Initialize the service with the required parameters to connect to the UAA

        Args:
            protocol: communications protocol
            host: UAA service host address
            port: UAA service port
        """
        self._protocol = protocol
        self._host = host
        self._port = int(port)

    async def validate_token(self, token: str) -> dict:
        """
        Request the JWT token validation to the associated UAA service

        Args:
            token: JWT token to validate

        Returns: user authenticated if the token is valid

        """
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
