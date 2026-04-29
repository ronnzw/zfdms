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

    def close_day(self, 
        deviceID: int,
        fiscalDayNo: int,
        fiscalDayCounters: list[dict],
        fiscalCounterType: str,
        fiscalCounterCurrency: str,
        fiscalCounterTaxPercent: int,
        fiscalCounterTaxID: int,
        fiscalCounterMoneyType: str,
        fiscalCounterValue: int,
        fiscalDayDeviceSignature: dict,
        receiptCounter: int,
    ) -> FiscalDayClose:
        """Initiate fiscal day closure procedure. This method is allowed when fiscal days status is “FiscalDayOpened” or “FiscalDayCloseFailed”. 
        
        In case fiscal day contains at least one “Grey” or “Red” receipt (as specified Validation errors), Fiscalisation Backend will respond to closeDay request with error (fiscal day will remain opened). Otherwise if fiscal day does not have “Grey” and “Red” receipts, validation of submitted closeDay request will be executed. 
        
        In case of fiscal day validation fails (as specified below in “Validation rules”), fiscal day remains opened and its status is changed to “FiscalDayCloseFailed”.

        :param deviceID: Device's Identification ID.
        :type  deviceID: ``int``

        :param fiscalDayNo: Fiscal day number. FiscalDayNo must be the same as provided/received fiscalDayNo value alue in openDay request.
        :type  fiscalDayNo: ``int``

        :param fiscalDayCounters: List of counters for each sale.
        :type  fiscalDayCounters: ``list``

        :param fiscalCounterType: Fiscal counter type.
        :type  fiscalCounterType: ``str``

        :param fiscalCounterCurrency: Fiscal counter currency (ISO 4217 currency code).
        :type  fiscalCounterCurrency: ``str``

        :param fiscalCounterTaxID: Tax ID of fiscal counter. Must be provided for all fiscal counter types “byTax”.
        :type  fiscalCounterTaxID: ``int``

        :param fiscalCounterTaxPercent: Tax percentage of fiscal counter.
        :type  fiscalCounterTaxPercent: ``int``

        :param fiscalCounterMoneyType: Code of payment mean of fiscal counter.
        :type  fiscalCounterMoneyType: ``str``

        :param fiscalCounterValue: Fiscal counter value in counter currency.
        :type  fiscalCounterValue: ``int``

        :param receiptCounter: ReceiptCounter value of last receipt of current fiscal day.
        :type  receiptCounter: ``int``


        :return: A FiscalDayClose dataclass instance with details about the closed day.
        :rtype: FiscalDayClose
        :raises FDMSApiException: If the API returns an error response.       
        """

        params = {
            "deviceID": deviceID,
            "fiscalDayNo": fiscalDayNo,
            "fiscalDayCounters": fiscalDayCounters,
            "fiscalCounterType": fiscalCounterType,
            "fiscalCounterCurrency": fiscalCounterCurrency,
        }

        if fiscalCounterTaxPercent:
            params.update({"fiscalCounterTaxPercent": fiscalCounterTaxPercent})
        elif fiscalCounterTaxID:
            params.update({"fiscalCounterTaxID": fiscalCounterTaxID})
        elif fiscalCounterMoneyType:
            params.update({"fiscalCounterMoneyType": fiscalCounterMoneyType})
        else:
            pass
        
        fiscal_day = self.client.post(
            f'{self.deviceID}/CloseDay', 
            {'data': params}
        )
        return parse_data(fiscal_day, FiscalDayClose)


# class Ronald:
#     def pass_data(self, data: dict, obj: object) -> object:
#         self.data, self.obj = data, obj
#         return parse_data(self.data, self.obj)


