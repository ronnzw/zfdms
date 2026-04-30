#!/usr/bin/env python
from datetime import datetime

import dacite
import requests

from .exceptions import FDMSApiException
from .models.get_config import DeviceConfig, DeviceOperatingMode
from .models.get_status import FiscalDay, FiscalDayServerSignature
from .utils import parse_data


class GetConfigClient:
    """Retrieves taxpayers and device information and
    configuration from the FDMS API."""

    def __init__(self, client):
        self.fdms_client = client

    def get_config(self, deviceID: int) -> DeviceConfig:
        """
        Retrieves taxpayers and device information and configurations.

        :param: deviceID Identifier of the device
        :rtype: ``int``

        :return: A DeviceConfig dataclass instance with the device configuration details.
        :rtype: DeviceConfig
        :raises FDMSApiException: If the API returns an error response.
        """
        self.deviceID = deviceID
        self.api_response = device_id_request(
            _method="GET", 
            client=self.fdms_client,
            deviceID=self.deviceID, 
            endPoint="GetConfig")

        if self.api_response and self.api_response != FDMSApiException:
            return parse_device_config(self.api_response)
        else:
            return self.api_response

    def parse_device_config(self, data: dict) -> DeviceConfig:
        """
        Parse a raw API response dict into a DeviceConfig dataclass.
        Handles nested objects, optional fields, and datetime parsing.
        """
        self.data = data
        return dacite.from_dict(
            data_class=DeviceConfig,
            data=self.data,
            config=dacite.Config(
                type_hooks={
                    datetime: lambda v: datetime.fromisoformat(v) if v else None,
                    DeviceOperatingMode: DeviceOperatingMode,
                },
                cast=[DeviceOperatingMode],
            )
        )
    



