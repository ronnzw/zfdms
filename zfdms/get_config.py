#!/usr/bin/env python
import requests

from dacite import from_dict
from datetime import datetime

from .exceptions import FDMSApiException
from .models.get_config import (DeviceConfig,
Address,
Contacts,
Tax, 
DeviceOperatingMode
)


class GetConfigClient(object):
    """Fetching configuration details for a device from the FDMS API."""
    
    def __init__(self, client):
        self.fdms_client = client

    def get_config(self, deviceID: int) -> DeviceConfig:
        """
        Fetch the device configuration from the FDMS API.

        :return: A DeviceConfig dataclass instance with the device configuration details.
        :rtype: DeviceConfig
        :raises FDMSApiException: If the API returns an error response.
        """
        try:
            response = self.fdms_client._make_request(
                method="GET",
                endpoint=f"/Device/v2/{deviceID}/GetConfig",
                auth_required=True,
            )
            response.raise_for_status()
            data = response.json()
            return self.parse_device_config(data=data)
        except requests.HTTPError as http_err:
            raise FDMSApiException.from_response(http_err.response) from http_err

    def parse_device_config(data: dict) -> DeviceConfig:
        """
        Parse a raw API response dict into a DeviceConfig dataclass.
        Handles nested objects, optional fields, and datetime parsing.
        """
        return dacite.from_dict(
            data_class=DeviceConfig,
            data=data,
            config=dacite.Config(
                type_hooks={
                    datetime: lambda v: datetime.fromisoformat(v) if v else None,
                    DeviceOperatingMode: DeviceOperatingMode,
                },
                cast=[DeviceOperatingMode],
            )
        )



