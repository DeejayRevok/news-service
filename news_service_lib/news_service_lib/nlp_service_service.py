"""
Module used to communicate with the NLP service
"""
from aiohttp import ClientSession
from aiohttp.web_exceptions import HTTPUnauthorized, HTTPInternalServerError
from news_service_lib import get_system_auth_token
from .models import New, NamedEntity, NLPDoc


class NlpServiceService:
    """
    NLP Service communicator service implementation
    """
    URL_BASE = '{protocol}://{host}:{port}/{path}'
    PATHS = {'hydrate_new': 'v1/api/nlp/hydrate',
             'process_text': 'v1/api/nlp'}

    def __init__(self, protocol: str, host: str, port: str):
        """
        Initialize the NLP service communicator

        Args:
            protocol: NLP service communications protocol
            host: NLP service host address
            port: NLP service port
        """
        self._protocol = protocol
        self._host = host
        self._port = int(port)

    async def hydrate_new(self, new: New):
        """
        Request the NLP service to hydrate the new with NLP information about the new

        Args:
            new: new to hydrate
        """
        system_auth_token = get_system_auth_token()
        async with ClientSession(headers={'X-API-Key': 'Bearer ' + system_auth_token}) as client:
            hydrate_new_url = self.URL_BASE.format(protocol=self._protocol, host=self._host, port=self._port,
                                                   path=self.PATHS['hydrate_new'])
            try:
                async with client.put(hydrate_new_url, data=dict(new)) as response:
                    if response.status == 401:
                        response_json = await response.json()
                        raise HTTPUnauthorized(reason=response_json['detail'])
                    elif response.status != 204:
                        response_json = await response.json()
                        raise HTTPInternalServerError(reason=response_json['detail'])

            except Exception as ex:
                if not isinstance(ex, HTTPUnauthorized) and not isinstance(ex, HTTPInternalServerError):
                    raise ConnectionError(f'Error calling NLP service {str(ex)}')
                else:
                    raise ex

    async def process_text(self, text: str) -> NLPDoc:
        """
        Request the NLP service to apply NLP processing in the given text

        Args:
            text: text to process

        Returns: NLP Doc with the extracted NLP data from the text
        """
        system_auth_token = get_system_auth_token()
        process_text_url = self.URL_BASE.format(protocol=self._protocol, host=self._host, port=self._port,
                                                path=self.PATHS['process_text'])
        async with ClientSession(headers={'X-API-Key': 'Bearer ' + system_auth_token}) as client:
            try:
                async with client.post(process_text_url, data=dict(text=text)) as response:
                    if response.status == 200:
                        response_content = await response.json()
                        return NLPDoc(sentences=response_content['sentences'],
                                      named_entities=response_content['named_entities'])
                    if response.status == 401:
                        response_json = await response.json()
                        raise HTTPUnauthorized(reason=response_json['detail'])
                    else:
                        response_json = await response.json()
                        raise HTTPInternalServerError(reason=response_json['detail'])

            except Exception as ex:
                if not isinstance(ex, HTTPUnauthorized) and not isinstance(ex, HTTPInternalServerError):
                    raise ConnectionError(f'Error calling NLP service {str(ex)}')
                else:
                    raise ex
