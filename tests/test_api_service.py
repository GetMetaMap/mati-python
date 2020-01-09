from contextlib import contextmanager

import pytest
import io

from mati import ApiService
from mati.call_http import ErrorResponse
from mati.types import (
    DocumentType,
    Input,
    InputsData,
    MediaInputOptions,
    PageType,
    PhotoInputData,
    SelfieVideoInputData,
    VerificationInputType,
)

client_id: str = 'clientId'
client_secret: str = 'clientSecret'
webhook_secret: str = 'webhookSecret'

webhook_resource_str = '{' \
                       '"eventName":"verification_completed",' \
                       '"metadata":{"email":"john@gmail.com"},' \
                       '"resource":"https://api.getmati.com/api/v1/verifications/db8d24783"' \
                       '}'

resource_url = 'http://resourceUrl'

def fetch_resource():
    api_service = ApiService()
    api_service.init(client_id, client_secret)
    return api_service.fetch_resource(resource_url)


@contextmanager
def not_raises(ExpectedException):
    try:
        yield

    except ExpectedException as error:
        raise AssertionError(f"Raised exception {error} when it should not!")

    except Exception as error:
        raise AssertionError(f"An unexpected exception {error} raised.")


def test_api_service_init():
    api_service = ApiService()
    with not_raises(None):
        api_service.init(client_id, client_secret, webhook_secret)


def test_api_service_validate_signature():
    api_service = ApiService()
    api_service.init(client_id, client_secret, webhook_secret)
    result = api_service.validate_signature(
        '0c5ed2cad914fd2a1571b47bb087953af574a353ff9d96f8603f8c0d7955340c',
        webhook_resource_str,
    )
    assert result is True


def test_api_service_validate_signature_no_secret():
    api_service = ApiService()
    api_service.init(client_id, client_secret)
    with pytest.raises(Exception):
        api_service.validate_signature('', '')


def test_api_service_validate_signature_wrong_signature():
    api_service = ApiService()
    api_service.init(client_id, client_secret, webhook_secret)
    result = api_service.validate_signature(
        'wrong sig',
        webhook_resource_str,
    )
    assert result is False


@pytest.mark.vcr
def test_api_service_fetch_resource():
    assert fetch_resource()


@pytest.mark.vcr
def test_api_service_fetch_resource_with_401_error():
    with pytest.raises(ErrorResponse):
        fetch_resource()


@pytest.mark.vcr
def test_api_service_create_identity():
    api_service = ApiService()
    api_service.init(client_id, client_secret)
    assert api_service.create_identity({'email': 'john@gmail.com'})


@pytest.mark.vcr
def test_api_service_send_input():
    api_service = ApiService()
    api_service.init(client_id, client_secret)
    inputs = [
        Input(
            input_type=VerificationInputType.document_photo,
            group=0,
            data=PhotoInputData(
                type=DocumentType.national_id,
                country='MX',
                page=PageType.front,
                filename='front.jpg'
            )
        ),
        Input(
            input_type=VerificationInputType.document_photo,
            group=0,
            data=PhotoInputData(
                type=DocumentType.national_id,
                country='MX',
                page=PageType.back,
                filename='back.jpg'
            )
        ),
        Input(
            input_type=VerificationInputType.selfie_video,
            data=SelfieVideoInputData(
                filename='selfie.mp4',
            )
        ),
    ]
    files = [
        MediaInputOptions('document', io.BytesIO()),
        MediaInputOptions('document', io.BytesIO()),
        MediaInputOptions('video', io.BytesIO()),
    ]
    assert api_service.send_input(
        identity_id='identityId',
        inputs_data=InputsData(files, inputs),
    )
