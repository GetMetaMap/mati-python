from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import BinaryIO, Dict, List, Optional, Union


class SerializableEnum(str, Enum):
    def __str__(self):
        return self.value


class PageType(SerializableEnum):
    front = 'front'
    back = 'back'


class VerificationInputType(SerializableEnum):
    document_photo = 'document-photo'
    selfie_photo = 'selfie-photo'
    selfie_video = 'selfie-video'


class DocumentType(SerializableEnum):
    driving_license = 'driving-license'
    national_id = 'national-id'
    passport = 'passport'
    proof_of_residency = 'proof-of-residency'


@dataclass
class VerificationStep:
    id: str
    status: int
    error: Optional[str] = None
    data: Optional[Dict] = field(default_factory=dict)


@dataclass
class VerificationDocument:
    country: str
    region: str
    photos: List[str]
    steps: List[VerificationStep]
    type: str
    fields: Optional[dict] = None


@dataclass
class UserValidationFile:
    filename: str
    content: BinaryIO
    input_type: Union[str, VerificationInputType]
    validation_type: Union[str, DocumentType] = ''
    country: str = ''  # alpha-2 code: https://www.iban.com/country-codes
    region: str = ''  # 2-digit US State code (if applicable)
    group: int = 0
    page: Union[str, PageType] = PageType.front


##########

IdentityMetadata = Union[dict, List[str]]


@dataclass
class MediaInputOptions:
    fieldName: str
    fileData: Union[BinaryIO, str]


@dataclass
class InputData:
    filename: str


@dataclass
class PhotoInputData(InputData):
    type: DocumentType
    page: PageType
    country: str
    region: str = None


@dataclass
class SelfieVideoInputData(InputData):
    pass


@dataclass
class SelfiePhotoInputData(InputData):
    pass


class Input(dict):
    def __init__(
            self,
            input_type: VerificationInputType,
            data: Union[PhotoInputData, SelfiePhotoInputData, SelfieVideoInputData],
            group: int = None
    ):
        if group is not None:
            dict.__init__(
                self,
                input_type=input_type,
                data=asdict(data),
                group=group,
            )
        else:
            dict.__init__(
                self,
                input_type=input_type,
                data=asdict(data),
            )


@dataclass
class SendInputRequest:
    files: List[MediaInputOptions]
    inputs: List[Input]


@dataclass
class IdentityStatusTypes(SerializableEnum):
    deleted = 'deleted',
    pending = 'pending',
    rejected = 'rejected',
    review_needed = 'reviewNeeded',
    running = 'running',
    verified = 'verified',


@dataclass
class IdentityResource:
    id: str
    status: IdentityStatusTypes


@dataclass
class EventNameTypes(SerializableEnum):
    step_completed = 'step_completed',
    verification_completed = 'verification_completed',
    verification_expired = 'verification_expired',
    verification_inputs_completed = 'verification_inputs_completed',
    verification_started = 'verification_started',
    verification_updated = 'verification_updated',


@dataclass
class WebhookResource:
    eventName: EventNameTypes
    metadata: IdentityMetadata
    resource: str


class AuthType(SerializableEnum):
    bearer = 'bearer'
    basic = 'basic'
    none = 'none'
