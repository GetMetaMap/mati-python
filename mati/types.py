from dataclasses import dataclass, field
from enum import Enum
from typing import BinaryIO, Dict, List, Optional, Union


class SerializableEnum(str, Enum):
    def __str__(self):
        return self.value


class PageType(SerializableEnum):
    front = 'front'
    back = 'back'


class ValidationInputType(SerializableEnum):
    document_photo = 'document-photo'
    selfie_photo = 'selfie-photo'
    selfie_video = 'selfie-video'


class ValidationType(SerializableEnum):
    driving_license = 'driving-license'
    national_id = 'national-id'
    passport = 'passport'
    proof_of_residency = 'proof-of-residency'


@dataclass
class VerificationDocumentStep:
    id: str
    status: int
    error: Optional[str] = None
    data: Optional[Dict] = field(default_factory=dict)


@dataclass
class VerificationDocument:
    country: str
    region: str
    photos: List[str]
    steps: List[VerificationDocumentStep]
    type: str
    fields: Optional[dict] = None


@dataclass
class UserValidationFile:
    filename: str
    content: BinaryIO
    input_type: Union[str, ValidationInputType]
    validation_type: Union[str, ValidationType] = ''
    country: str = ''  # alpha-2 code: https://www.iban.com/country-codes
    region: str = ''  # 2-digit US State code (if applicable)
    group: int = 0
    page: Union[str, PageType] = PageType.front


##########

IdentityMetadata = Union[dict, List[str]]

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
