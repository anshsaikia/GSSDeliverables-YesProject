import pytest

def pytest_addoption(parser):
    parser.addoption(
        '--device-number',
        action='store',
        default='0',
        type='int',
        help='Device number to use')
    parser.addoption(
        '--profile',
        action='store',
        default=None,
        type='string',
        help='Profile to use')
    parser.addoption(
        '--platform',
        action='store',
        default=None,
        type='string',
        help='platform to use')
