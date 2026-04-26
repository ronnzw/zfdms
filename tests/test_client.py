#!/usr/bin/env python
import pytest
import requests
from unittest.mock import MagicMock, patch, PropertyMock

from zfdms.client import FdmsClient
from zfdms.exceptions import (FDMSApiException, FDMSValidationException,)


@pytest.fixture
def client():
    """
    A fully instantiated FdmsClient with fake cert paths.
    We patch requests.Session so no real HTTP calls are made.
    """
    return FdmsClient(
        host="fdms.example.co.zw",
        device_id="SN-1",
        device_model_name="TestDevice",
        device_model_version_no="1.0.0",
        client_cert="/fake/device.crt",
        client_key="/fake/device.key",
        ca_cert="/fake/ca.crt",
    )


@pytest.fixture
def mock_response():
    """
    A factory fixture that builds a fake requests.Response.
    Call it with the data you want returned:
        mock_response({"key": "value"}, status_code=200)
    """
    def _make(data, status_code=200):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = data
        response.text = str(data)
        # Only raise on 4xx/5xx
        if status_code >= 400:
            http_error = requests.HTTPError(response=response)
            response.raise_for_status.side_effect = http_error
        else:
            response.raise_for_status.return_value = None
        return response
    return _make


@pytest.fixture
def error_response():
    """
    A factory fixture that builds a fake RFC 7807 error response.
    Call it with the FDMS error code you want to simulate:
        error_response("DEV01", status_code=422)
    """
    def _make(error_code, status_code=422, title="An error occurred"):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = {
            "type": f"https://fdms.example.co.zw/errors/{error_code}",
            "title": title,
            "status": status_code,
            "errorCode": error_code,
        }
        response.text = error_code
        http_error = requests.HTTPError(response=response)
        response.raise_for_status.side_effect = http_error
        return response
    return _make


class TestClientInit:

    def test_base_url_is_set_correctly(self, client):
        assert client.base_url == "https://fdms.example.co.zw/api/v1"

    def test_device_id_is_stored(self, client):
        assert client.device_id == "SN-1"

    def test_timeout_is_30_seconds(self, client):
        # Per FDMS spec all sync operations must timeout at 30s
        assert client.timeout == 30

    def test_authenticated_session_has_cert(self, client):
        assert client.session.cert == ("/fake/device.crt", "/fake/device.key")

    def test_public_session_has_no_cert(self, client):
        assert client.public_session.cert is None

    def test_authenticated_session_verify_ca(self, client):
        assert client.session.verify == "/fake/ca.crt"

    def test_public_session_verify_ca(self, client):
        assert client.public_session.verify == "/fake/ca.crt"

    def test_mandatory_headers_on_authenticated_session(self, client):
        headers = client.session.headers
        assert headers["DeviceModelName"] == "TestDevice"
        assert headers["DeviceModelVersionNo"] == "1.0.0"
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"

    def test_mandatory_headers_on_public_session(self, client):
        # DeviceModelName and DeviceModelVersionNo are mandatory on ALL requests
        headers = client.public_session.headers
        assert headers["DeviceModelName"] == "TestDevice"
        assert headers["DeviceModelVersionNo"] == "1.0.0"

    def test_skip_ssl_validation(self):
        client = FdmsClient(
            host="fdms.example.co.zw",
            device_id="SN-1",
            device_model_name="TestDevice",
            device_model_version_no="1.0.0",
            client_cert="/fake/device.crt",
            client_key="/fake/device.key",
            skip_ssl_validation=True,
        )
        assert client.session.verify is False
        assert client.public_session.verify is False

    def test_proxy_is_set_when_provided(self):
        client = FdmsClient(
            host="fdms.example.co.zw",
            device_id="SN-1",
            device_model_name="TestDevice",
            device_model_version_no="1.0.0",
            client_cert="/fake/device.crt",
            client_key="/fake/device.key",
            proxy="https://myproxy.co.zw",
        )
        assert client.session.proxies == {"https": "https://myproxy.co.zw"}
        assert client.public_session.proxies == {"https": "https://myproxy.co.zw"}

    def test_get_config_client_is_initialised(self, client):
        from zfdms.get_config import GetConfigClient
        assert isinstance(client._get_config, GetConfigClient)


class TestAuthenticatedGet:

    def test_get_returns_json(self, client, mock_response):
        payload = {"operationID": "ABC123"}
        client.session.get = MagicMock(return_value=mock_response(payload))

        result = client.get("device/SN-1/config")

        assert result == payload

    def test_get_calls_correct_url(self, client, mock_response):
        client.session.get = MagicMock(return_value=mock_response({}))

        client.get("device/SN-1/config")

        client.session.get.assert_called_once_with(
            "https://fdms.example.co.zw/api/v1/device/SN-1/config",
            params=None,
            timeout=30,
        )

    def test_get_passes_query_params(self, client, mock_response):
        client.session.get = MagicMock(return_value=mock_response({}))

        client.get("device/SN-1/config", params={"include": "taxes"})

        client.session.get.assert_called_once_with(
            "https://fdms.example.co.zw/api/v1/device/SN-1/config",
            params={"include": "taxes"},
            timeout=30,
        )

    def test_get_uses_authenticated_session_not_public(self, client, mock_response):
        client.session.get = MagicMock(return_value=mock_response({}))
        client.public_session.get = MagicMock()

        client.get("device/SN-1/config")

        client.session.get.assert_called_once()
        client.public_session.get.assert_not_called()


class TestAuthenticatedPost:

    def test_post_returns_json(self, client, mock_response):
        payload = {"receiptId": "R001"}
        client.session.post = MagicMock(return_value=mock_response(payload))

        result = client.post("device/SN-1/receipt", data={"amount": 100})

        assert result == payload

    def test_post_calls_correct_url(self, client, mock_response):
        client.session.post = MagicMock(return_value=mock_response({}))

        client.post("device/SN-1/receipt", data={"amount": 100})

        client.session.post.assert_called_once_with(
            "https://fdms.example.co.zw/api/v1/device/SN-1/receipt",
            json={"amount": 100},
            timeout=30,
        )

    def test_post_uses_authenticated_session_not_public(self, client, mock_response):
        client.session.post = MagicMock(return_value=mock_response({}))
        client.public_session.post = MagicMock()

        client.post("device/SN-1/receipt")

        client.session.post.assert_called_once()
        client.public_session.post.assert_not_called()


class TestPublicGet:

    def test_public_get_returns_json(self, client, mock_response):
        payload = {"certificate": "abc123"}
        client.public_session.get = MagicMock(return_value=mock_response(payload))

        result = client.public_get("certificate/server")

        assert result == payload

    def test_public_get_uses_public_session_not_authenticated(self, client, mock_response):
        client.public_session.get = MagicMock(return_value=mock_response({}))
        client.session.get = MagicMock()

        client.public_get("certificate/server")

        client.public_session.get.assert_called_once()
        client.session.get.assert_not_called()


class TestPublicPost:

    def test_public_post_returns_json(self, client, mock_response):
        payload = {"deviceId": "SN-1", "status": "registered"}
        client.public_session.post = MagicMock(return_value=mock_response(payload))

        result = client.public_post("device/register", data={"serialNo": "SN-1"})

        assert result == payload

    def test_public_post_uses_public_session_not_authenticated(self, client, mock_response):
        client.public_session.post = MagicMock(return_value=mock_response({}))
        client.session.post = MagicMock()

        client.public_post("device/register")

        client.public_session.post.assert_called_once()
        client.session.post.assert_not_called()


class TestErrorHandling:

    def test_raises_fdms_api_exception_on_400(self, client, error_response):
        client.session.get = MagicMock(return_value=error_response("DEV01", status_code=400))

        with pytest.raises(FDMSApiException) as exc_info:
            client.get("device/SN-1/config")

        assert exc_info.value.status_code == 400
        assert exc_info.value.error_code == "DEV01"

    def test_raises_fdms_api_exception_on_401(self, client, error_response):
        client.session.get = MagicMock(return_value=error_response("DEV01", status_code=401))

        with pytest.raises(FDMSApiException) as exc_info:
            client.get("device/SN-1/config")

        assert exc_info.value.status_code == 401

    def test_raises_fdms_api_exception_on_422_dev_error(self, client, error_response):
        client.session.post = MagicMock(return_value=error_response("DEV05", status_code=422))

        with pytest.raises(FDMSApiException) as exc_info:
            client.post("device/SN-1/receipt")

        assert exc_info.value.error_code == "DEV05"

    def test_raises_validation_exception_for_rcpt_error(self, client, error_response):
        client.session.post = MagicMock(return_value=error_response("RCPT011", status_code=422))

        with pytest.raises(FDMSValidationException) as exc_info:
            client.post("device/SN-1/receipt")

        assert exc_info.value.error_code == "RCPT011"
        assert exc_info.value.status_code == 422

    def test_validation_exception_has_correct_color(self, client, error_response):
        client.session.post = MagicMock(return_value=error_response("RCPT011", status_code=422))

        with pytest.raises(FDMSValidationException) as exc_info:
            client.post("device/SN-1/receipt")

        # RCPT011 is a Red error per spec
        assert exc_info.value.color == "Red"

    def test_retryable_on_500(self, client, error_response):
        client.session.get = MagicMock(return_value=error_response("", status_code=500))

        with pytest.raises(FDMSApiException) as exc_info:
            client.get("device/SN-1/config")

        assert exc_info.value.should_retry is True

    def test_retryable_on_502(self, client, error_response):
        client.session.get = MagicMock(return_value=error_response("", status_code=502))

        with pytest.raises(FDMSApiException) as exc_info:
            client.get("device/SN-1/config")

        assert exc_info.value.should_retry is True

    def test_not_retryable_on_422(self, client, error_response):
        client.session.post = MagicMock(return_value=error_response("DEV01", status_code=422))

        with pytest.raises(FDMSApiException) as exc_info:
            client.post("device/SN-1/receipt")

        assert exc_info.value.should_retry is False

    def test_exception_includes_uri(self, client, error_response):
        client.session.get = MagicMock(return_value=error_response("DEV04", status_code=422))

        with pytest.raises(FDMSApiException) as exc_info:
            client.get("device/SN-1/config")

        assert exc_info.value.uri == "device/SN-1/config"

    def test_exception_str_includes_error_code(self, client, error_response):
        client.session.get = MagicMock(return_value=error_response("DEV04", status_code=422))

        with pytest.raises(FDMSApiException) as exc_info:
            client.get("device/SN-1/config")

        assert "DEV04" in str(exc_info.value)

    def test_handles_non_json_error_body_gracefully(self, client):
        response = MagicMock()
        response.status_code = 500
        response.text = "Internal Server Error"
        response.json.side_effect = ValueError("No JSON")
        response.raise_for_status.side_effect = requests.HTTPError(response=response)
        client.session.get = MagicMock(return_value=response)

        with pytest.raises(FDMSApiException) as exc_info:
            client.get("device/SN-1/config")

        assert exc_info.value.status_code == 500
        assert exc_info.value.error_code is None


# ── get_config property test 
class TestGetConfigProperty:

    def test_get_config_property_returns_same_instance(self, client):
        assert client.get_config is client.get_config

    def test_get_config_property_returns_get_config_client(self, client):
        from zfdms.get_config import GetConfigClient
        assert isinstance(client.get_config, GetConfigClient)