#!/usr/bin/env python
import requests

from .exceptions import FDMSApiException, FDMSValidationException
from .fiscal_day import FiscalDayClient
from .get_config import GetConfigClient
from .receipts import ReceiptsClient
from .submit_file import SubmitFileClient
from .certificates import CertificatesClient


class FdmsClient:
    """
    The main Fiscal Device Gateway API client.

    All methods are synchronous except:
        - closeDay    (async processing, sync acknowledgement)
        - submitFile  (async processing, sync acknowledgement)

    Uses mutual TLS (mTLS) for authenticated endpoints.

    Public endpoints (no certificate required):
        - 4.1  verifyTaxpayerInformation
        - 4.2  registerDevice
        - 4.12 getServerCertificate

    All other endpoints require a valid, non-revoked, non-expired
    device certificate issued by FDMS for the calling device.
    """

    def __init__(
        self,
        host,
        device_id,
        device_model_name,
        device_model_version_no,
        client_cert,
        client_key,
        ca_cert=None,
        proxy=None,
        skip_ssl_validation=False,
    ):
        """
        Instantiate a new FDMS API client.

        :param host: The FDMS gateway host, e.g. "fdms.example.co.zw"
        :type  host: ``str``

        :param device_id: The fiscal device ID used in authenticated requests
        :type  device_id: ``str``

        :param device_model_name: Device model name as registered in ZIMRA
        :type  device_model_name: ``str``

        :param device_model_version_no: Device model version number as registered in ZIMRA
        :type  device_model_version_no: ``str``

        :param client_cert: Path to the device certificate file (.pem / .crt)
        :type  client_cert: ``str``

        :param client_key: Path to the device private key file (.pem / .key)
        :type  client_key: ``str``

        :param ca_cert: Path to the FDMS CA certificate for server verification.
                        If None, the system CA store is used.
        :type  ca_cert: ``str``

        :param proxy: Optional proxy URL to connect through
        :type  proxy: ``str``

        :param skip_ssl_validation: Skip SSL certificate validation (not recommended in production)
        :type  skip_ssl_validation: ``bool``
        """
        self.device_id = device_id
        self.base_url = f"https://{host}/Device/v1"
        self.timeout = 30

        # Public session (no client certificate)
        self.public_session = requests.Session()

        # Authenticated session (mTLS)
        self.session = requests.Session()
        self.session.cert = (client_cert, client_key)

        for s in (self.session, self.public_session):
            if proxy:
                s.proxies = {"https": proxy}

            if skip_ssl_validation:
                s.verify = False
            elif ca_cert:
                s.verify = ca_cert


            s.headers.update(
                {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "DeviceModelName": device_model_name,
                    "DeviceModelVersionNo": device_model_version_no,
                }
            )

            self._get_config = GetConfigClient(self)
            self._fiscal_day = FiscalDayClient(self)
            self._receipts = ReceiptsClient(self)
            self._submit_file = SubmitFileClient(self)
            self._server_requests = CertificatesClient(self)

    def get(self, uri, params=None):
        """
        Perform an authenticated GET request.

        :param uri: Relative URI, e.g. "device/SN-1/config"
        :type  uri: ``str``

        :param params: Optional query parameters
        :type  params: ``dict``
        """
        try:
            result = self.session.get(
                f"{self.base_url}/{uri}",
                params=params,
                timeout=self.timeout,
            )
            result.raise_for_status()
            return result.json()
        except requests.HTTPError as e:
            self._handle_error(e, uri)

    def post(self, uri, data=None):
        """
        Perform an authenticated POST request.

        :param uri: Relative URI
        :type  uri: ``str``

        :param data: Request body payload
        :type  data: ``dict``
        """
        try:
            result = self.session.post(
                f"{self.base_url}/{uri}",
                json=data,
                timeout=self.timeout,
            )
            result.raise_for_status()
            return result.json()
        except requests.HTTPError as e:
            self._handle_error(e, uri)

    def public_get(self, uri, params=None):
        """
        Perform a public (unauthenticated) GET request.

        :param uri: Relative URI
        :type  uri: ``str``

        :param params: Optional query parameters
        :type  params: ``dict``
        """
        try:
            result = self.public_session.get(
                f"{self.base_url}/{uri}",
                params=params,
                timeout=self.timeout,
            )
            result.raise_for_status()
            return result.json()
        except requests.HTTPError as e:
            self._handle_error(e, uri)

    def public_post(self, uri, data=None):
        """
        Perform a public (unauthenticated) POST request.

        :param uri: Relative URI
        :type  uri: ``str``

        :param data: Request body payload
        :type  data: ``dict``
        """
        try:
            result = self.public_session.post(
                f"{self.base_url}/{uri}",
                json=data,
                timeout=self.timeout,
            )
            result.raise_for_status()
            return result.json()
        except requests.HTTPError as e:
            self._handle_error(e, uri)

    def _handle_error(self, e, uri=None):
            """
            Parse RFC 7807 Problem Details response and raise the appropriate exception.
            Raises FDMSValidationException for receipt validation errors (RCPT0xx),
            FDMSApiException for all other errors.
            """
            status_code = e.response.status_code
            message = e.response.text
            error_code = None
            title = None

            try:
                body = e.response.json()
                error_code = body.get("errorCode") or body.get("code")
                title = body.get("title")
            except Exception:
                pass

            # Route to validation exception for receipt validation error codes
            if error_code and error_code.startswith("RCPT0"):
                raise FDMSValidationException(
                    status_code=status_code,
                    message=message,
                    uri=uri,
                    error_code=error_code,
                    title=title,
                )

            raise FDMSApiException(
                status_code=status_code,
                message=message,
                uri=uri,
                error_code=error_code,
                title=title,
            )

    @property
    def get_config(self):
        """
        Get the GetConfigClient for fetching device configuration details.

        :rtype: :class:`zfdms.get_config.GetConfigClient`
        """
        return self._get_config

    @property
    def fiscal_day(self):
        """
        Get the FiscalDayClient for managing fiscal day operations.

        :rtype: :class:`zfdms.fiscal_day.FiscalDayClient`
        """
        return self._fiscal_day

    @property
    def receipts(self):
        """
        Get the ReceiptsClient for managing receipt operations.

        :rtype: :class:`zfdms.receipts.ReceiptsClient`
        """
        return self._receipts

    @property
    def submit_file(self):
        """
        Get the SubmitFileClient for managing file submission and status.

        :rtype: :class:`zfdms.submit_file.SubmitFileClient`
        """
        return self._submit_file        

    @property
    def get_file_status(self):
        """
        :rtype: :class:`zfdms.get_file_status.GetFileStatusClient`
        """
        return self._get_file_status

    @property
    def server_requests(self):
        """
        Get the CertificatesClient for managing server certificate operations.

        :rtype: :class:`zfdms.certificates.CertificatesClient`
        """
        return self._server_requests
