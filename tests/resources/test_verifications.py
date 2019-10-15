import os

import pytest

from mati import Client


@pytest.mark.skipif(
    os.getenv('VCR_UNSAFE') != 'true', reason="can't record this yet"
)
def test_verifications(client: Client):
    verification = client.verifications.retrieve('5d9fb1f5bfbfac001a349bfb')
    assert verification
