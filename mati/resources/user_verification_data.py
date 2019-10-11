import json
from dataclasses import dataclass
from typing import ClassVar, List

from ..types import UserValidationFile
from .base import Resource


def get_file_type(input_type: str) -> str:
    if input_type == 'selfie-video':
        file_type = 'video'
    elif input_type == 'selfie-photo':
        file_type = 'selfie'
    else:
        file_type = 'document'
    return file_type


@dataclass
class UserValidationData(Resource):
    """
    Based on: https://docs.getmati.com/#step-3-upload-user-verification-data
    """

    _endpoint: ClassVar[str] = '/v2/identities/{identity_id}/send-input'

    @classmethod
    def upload(
        cls, identity_id: str, user_validation_files: List[UserValidationFile]
    ) -> List[dict]:
        endpoint = cls._endpoint.format(identity_id=identity_id)
        files_metadata = []
        multiple_files = []
        for file in user_validation_files:
            files_metadata.append(
                dict(
                    inputType=file.input_type,
                    group=file.group,
                    data=dict(
                        type=file.validation_type,
                        country=file.country,
                        page=file.page,
                        filename=file.filename,
                        region=file.region,
                    ),
                )
            )
            multiple_files.append(('document', open(file.content.name, 'rb')))
        resp = cls._client.post(
            endpoint,
            data=dict(inputs=json.dumps(files_metadata)),
            files=multiple_files,
        )
        return resp
