from mati.types import VerificationInputType


def test_type_to_str():
    assert str(VerificationInputType.document_photo) == 'document-photo'
    assert VerificationInputType.document_photo == 'document-photo'
