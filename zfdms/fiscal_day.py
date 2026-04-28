#!/usr/bin/env python
import dacite
import requests

from datetime import datetime

from .exceptions import FDMSApiException
from .utils import device_id_request, parse_data
from .models.fiscal_day import (
    FiscalDay, 
    FiscalDayServerSignature,
    FiscalDayOpen,
    FiscalDayClose,
    FiscalDayCounter,
    DeviceOperatingMode,
)


class FiscalDayClient:
    """Fiscal day API"""

    def __init__(self, client):
        self.fdms_client = client

    def get_status(self, deviceID: int) -> FiscalDay:
        """
        Get fiscal day status.

        :param deviceID: Device's Identification ID.
        :type  deviceID: ``int``

        :return: A FiscalDay dataclass instance with the fiscal day status.
        :rtype: FiscalDay
        :raises FDMSApiException: If the API returns an error response.
        """
        self._api_response = device_id_request("GET", self.fdms_client, self.deviceID,"GetStatus")
        if self._api_response and self._api_response != FDMSApiException:
            return self.parse_device_config(self.           _api_response)
        else:
            return self._api_response

    def open_day(self, deviceID: int) -> FiscalDayOpen:
        """Opens a fiscal day in fdms.

        :param deviceID: Device's Identification ID.
        :type  deviceID: ``int``

        :return: A FiscalDayOpen dataclass instance with details about the opened day.
        :rtype: FiscalDayOpen
        :raises FDMSApiException: If the API returns an error response.       
        """
        self.deviceID = deviceID
        self.api_response = device_id_request(
            _method="POST", 
            client=self.fdms_client,
            deviceID=self.deviceID, 
            endPoint="OpenDay")

        if self.api_response and self.api_response != FDMSApiException:
            return parse_data(self.api_response, FiscalDayOpen)
        else:
            return self.api_response


# class Ronald:
#     def pass_data(self, data: dict, obj: object) -> object:
#         self.data, self.obj = data, obj
#         return parse_data(self.data, self.obj)


