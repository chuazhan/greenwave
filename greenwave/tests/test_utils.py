
# SPDX-License-Identifier: GPL-2.0+

import pytest

import json

from requests import ConnectionError, ConnectTimeout
from werkzeug.exceptions import InternalServerError

import greenwave.app_factory
from greenwave.utils import json_error, retry


def test_retry_passthrough():
    """ Ensure that retry doesn't gobble exceptions. """
    expected = "This is the exception."

    @retry(timeout=0.1, interval=0.1, wait_on=Exception)
    def f():
        raise Exception(expected)

    with pytest.raises(Exception) as actual:
        f()

    assert expected in str(actual)


def test_retry_count():
    """ Ensure that retry doesn't gobble exceptions. """
    expected = "This is the exception."

    calls = []

    @retry(timeout=0.3, interval=0.1, wait_on=Exception)
    def f():
        calls.append(1)
        raise Exception(expected)

    with pytest.raises(Exception):
        f()

    assert sum(calls) == 3


@pytest.mark.parametrize('error, expected_error_message_part', [
    (ConnectionError('ERROR'), 'ERROR'),
    (ConnectTimeout('TIMEOUT'), 'TIMEOUT'),
    (InternalServerError(), 'The server encountered an internal error'),
])
def test_json_error(error, expected_error_message_part):
    app = greenwave.app_factory.create_app()
    with app.app_context():
        with app.test_request_context():
            r = json_error(error)
            data = json.loads(r.get_data())
            assert r.status_code == 500
            assert expected_error_message_part in data['message']
