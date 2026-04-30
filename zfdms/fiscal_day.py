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
        self.client = client

    def get_status(self, deviceID: int) -> FiscalDay:
        """
        Get fiscal day status.

        :param deviceID: Device's Identification ID.
        :type  deviceID: ``int``

        :return: A FiscalDay dataclass instance with the fiscal day status.
        :rtype: FiscalDay
        :raises FDMSApiException: If the API returns an error response.
        """
        device_status = self.client.get(f'{self.deviceID}/GetStatus')

        if device_status and device_status != FDMSApiException:
            return self.parse_device_config(device_status,FiscalDay)
        else:
            return device_status

    def open_day(self, 
        deviceID: int,
        fiscalDayNo: int,
        fiscalDayOpened: datetime,
    ) -> FiscalDayOpen:
        """Open a fiscal day in fdms.

        :param deviceID: Device's Identification ID.
        :type  deviceID: ``int``

        :param fiscalDayNo: Fiscal day count.
        :type  fiscalDayNo: ``int``

        :param fiscalDayOpened: Date and time when you opened day
        :type  fiscalDayOpened: ``datetime``

        :return: A FiscalDayOpen dataclass instance with details about the opened day.
        :rtype: FiscalDayOpen
        :raises FDMSApiException: If the API returns an error response.       
        """
        params = {
            "fiscalDayNo": fiscalDayNo,
            "fiscalDayOpened": fiscalDayOpened,
        }

        fiscal_day = self.client.post(
            f'{self.deviceID}/OpenDay', 
            {'data': params}
        )
        return parse_data(fiscal_day, FiscalDayOpen)

    def close_day(
        self,
        deviceID: int,
        fiscalDayNo: int,
        fiscalDayCounters: list[dict],
        fiscalDayDeviceSignature: dict,
        receiptCounter: int,
    ) -> FiscalDayClose:
        """
        Initiate fiscal day closure procedure.

        This method is allowed when fiscal day status is "FiscalDayOpened" or
        "FiscalDayCloseFailed". This method is asynchronous — FDMS acknowledges
        the request synchronously but processes it asynchronously.

        If the fiscal day contains at least one "Grey" or "Red" receipt, FDMS
        will respond with an error and the fiscal day will remain opened.

        If fiscal day validation fails, the fiscal day remains opened and its
        status is changed to "FiscalDayCloseFailed".

        Note: Zero value counters must not be submitted in fiscalDayCounters.
        Note: Cannot be sent if DeviceOperatingMode is Offline (returns DEV01).

        :param deviceID: Device identification ID.
        :type  deviceID: ``int``

        :param fiscalDayNo: Fiscal day number. Must match the fiscalDayNo
                            received in the openDay request.
        :type  fiscalDayNo: ``int``

        :param fiscalDayCounters: List of fiscal counters for the day.
                                Each counter must include fiscalCounterType,
                                fiscalCounterCurrency and fiscalCounterValue.
                                fiscalCounterTaxID and fiscalCounterTaxPercent
                                are required for "byTax" counter types.
                                fiscalCounterMoneyType is required for
                                "BalanceByMoneyType" counter type.
                                Zero value counters must not be submitted.
        :type  fiscalDayCounters: ``list[dict]``

        :param fiscalDayDeviceSignature: SHA256 hash of fiscal day report fields
                                        and device signature using device private key.
        :type  fiscalDayDeviceSignature: ``dict``

        :param receiptCounter: receiptCounter value of the last receipt of the current fiscal day.
        :type  receiptCounter: ``int``

        :return: A FiscalDayClose dataclass instance with the operation details.
        :rtype: FiscalDayClose

        :raises FDMSApiException: If the API returns an error response.
        :raises FDMSValidationException: If fiscal day validation fails (FISC03, FISC04).
        """

        params = {
            "fiscalDayNo": fiscalDayNo,
            "fiscalDayCounters": fiscalDayCounters,
            "fiscalDayDeviceSignature": fiscalDayDeviceSignature,
            "receiptCounter": receiptCounter,
        }

        fiscal_day = self.client.post(
            f"{deviceID}/CloseDay",
            params,
        )
        return parse_data(fiscal_day, FiscalDayClose)


# class Ronald:
#     def pass_data(self, data: dict, obj: object) -> object:
#         self.data, self.obj = data, obj
#         return parse_data(self.data, self.obj)


