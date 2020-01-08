import hashlib
import hmac
from base64 import b64encode
from typing import Optional

from mati.call_http import RequestOptions, call_http, ErrorResponse
from mati.types import AuthType, IdentityMetadata, IdentityResource

API_HOST = 'https://api.getmati.com'


class ApiService:
    bearer_auth_header: str = None
    client_auth_header: str = None
    host: str
    webhook_secret: Optional[str]

    def init(self, client_id: str, client_secret: str, webhook_secret: str = None, host: str = None):
        """
        Initializes the service. Call this method before using api calls.
        ---------
        :param str client_id:
        :param str client_secret:
        :param str host:
        :param str webhook_secret:
        :return: None
        """
        self.host = host or API_HOST
        self.webhook_secret = webhook_secret or None
        self._set_client_auth(client_id, client_secret)

    def validate_signature(self, signature: str, body_str: str):
        """
        Validates signature of requests.
        We use webhookSecret to sign data. You put this value in the Dashboard, when define webhooks.
        And provide the same value, when you initialize the service. Please, use a strong secret value.
        Draw your attention. The order of the fields in the body is important. Keep the original one.
        ---------
        :param str signature: signature from x-signature header of request calculated on Mati side
        :param str body_str: data came in request body
        :raise: Exception if `webhook_secret` is not provided
        :return: bool `true` if the signature is valid, `false` - otherwise
        """
        if self.webhook_secret is None:
            raise Exception('No webhookSecret provided')
        dig = hmac.new(self.webhook_secret.encode(), msg=body_str.encode(), digestmod=hashlib.sha256)
        return signature == dig.hexdigest()

    def fetch_resource(self, url: str):
        """
        Fetches resource by its absolute URL using your client credentials you provide,
        when you initialize the service. Usually you do not need to build url by yourself,
        its values come in webhooks or in other resources.

        :param url: absolute url of the resource
        :return: resource
        :raise ErrorResponse if we get http error
        """
        return self._call_http(url=url)

    def create_identity(self, metadata: IdentityMetadata) -> IdentityResource:
        """
        Starts new verification flow and creates identity. You should use result of this method
        in order to get id for further `#sendInput` calls.

        :param {IdentityMetadata} metadata: payload you want to pass to the identity
        :return: resource of identity created.
        :raise ErrorResponse if we get http error
        """
        return self._call_http(
            path='v2/identities',
            request_options=RequestOptions(
                method='post',
                body={'metadata': metadata}
            )
        )

    def _set_client_auth(self, client_id, client_secret):
        auth = b64encode(f'{client_id}:{client_secret}'.encode('utf-8'))
        self.client_auth_header = 'Basic ' + auth.decode('ascii')

    def _set_bearer_auth(self, access_token):
        self.bearer_auth_header = f'Bearer {access_token}'

    def auth(self):
        auth_response = self._call_http(
            path='oauth',
            auth_type=AuthType.basic,
            request_options=RequestOptions(
                method='post',
                body={'grant_type': 'client_credentials'},
                headers={'content-type': 'application/x-www-form-urlencoded'},
            )
        )
        self._set_bearer_auth(auth_response['access_token'])
        return auth_response

    def _call_http(
            self,
            path: str = None,
            url: str = None,
            request_options: RequestOptions = RequestOptions(),
            auth_type: AuthType = AuthType.bearer,
    ):
        tried_auth = False
        if auth_type == AuthType.bearer and self.bearer_auth_header is None:
            self.auth()
            tried_auth = True
        if auth_type != AuthType.none:
            authorization = None
            if auth_type == AuthType.bearer:
                authorization = self.bearer_auth_header
            elif auth_type == AuthType.basic:
                authorization = self.client_auth_header
            if authorization is not None:
                headers = request_options.headers or dict()
                headers['Authorization'] = authorization
                request_options.headers = headers
        request_url = url or f'{self.host}/{path}'
        try:
            return call_http(request_url, request_options)
        except ErrorResponse as err:
            if not tried_auth and auth_type == AuthType.bearer and err.response.status_code == 401:
                self.auth()
                request_options.headers['Authorization'] = self.bearer_auth_header
                return call_http(request_url, request_options)
            raise err
