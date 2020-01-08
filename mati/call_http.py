from typing import Dict, Union
from requests_toolbelt import MultipartEncoder

from attr import dataclass
from requests import Session, Response

session = Session()


@dataclass
class RequestOptions:
    method: str = 'get'
    headers: Dict[str, str] = None
    body: Union[Dict, MultipartEncoder] = None
    data: Dict = None


class ErrorResponse(Exception):
    message: str
    response: Response


def call_http(request_url: str, request_options: RequestOptions):
    response = session.request(
        request_options.method,
        request_url,
        headers=request_options.headers,
        data=request_options.data,
    )
    if not response.ok:
        print(f'response.text: {response.text}')
        raise ErrorResponse(response.text, response)
    return response.json()
