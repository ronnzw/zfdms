import dacite
import requests

from datetime import datetime

from .exceptions import FDMSApiException
from .utils import device_id_request, parse_data
from .models.server_certs import (
RenewCertificate, 
ServerCert, 
PingResponse,
) 


class CertificatesClient:
    """Certificates API"""

    def __init__(self, client):
        self.client = client

    def renew_certificate(self, deviceID: int) -> RenewCertificate:
        """
        Renew the server certificate for a device.

        :param deviceID: Device's Identification ID.
        :type  deviceID: ``int``

        :return: A RenewCertificate dataclass instance with the renewed certificate details.
        :rtype: RenewCertificate
        :raises FDMSApiException: If the API returns an error response.
        """
        response = self.client.post(
            f"{deviceID}/IssueCertificate"
        )
        return parse_data(response, RenewCertificate)

    def get_server_certificate(self, deviceID: int) -> ServerCert:
        """
        Retrieve the current server certificate for a device.

        :param deviceID: Device's Identification ID.
        :type  deviceID: ``int``

        :return: A ServerCert dataclass instance with the current server certificate details.
        :rtype: ServerCert
        :raises FDMSApiException: If the API returns an error response.
        """
        response = self.client.get(
            f"{deviceID}/GetServerCertificate"
        )
        return parse_data(response, ServerCert)

        def ping(self, deviceID: int) -> PingResponse:
        """
        Ping the FDMS server to check connectivity and authentication.

        :param deviceID: Device's Identification ID.
        :type  deviceID: ``int``

        :return: A PingResponse dataclass instance with the ping results.
        :rtype: PingResponse
        :raises FDMSApiException: If the API returns an error response.
        """
        response = self.client.get(
            f"{deviceID}/Ping"
        )
        return parse_data(response, PingResponse)