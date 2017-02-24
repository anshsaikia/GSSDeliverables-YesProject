from tests_framework.ve_tests.ve_test import VeTestApi
import pytest

@pytest.mark.healthcheck_device
def test_healthcheck_device():
    test = VeTestApi("test_healthcheck_device", vgwUtils=False)
    test.healthcheck()

@pytest.mark.healthcheck_network
def test_healthcheck_network():
    test = VeTestApi("test_healthcheck_network")
    test.retrieve_he_info()

@pytest.mark.healthcheck_code
def test_healthcheck_code():
    test = VeTestApi("test_healthcheck_code")
    test.codecheck()
