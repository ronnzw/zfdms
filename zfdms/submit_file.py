import dacite
import requests

from datetime import datetime

from .exceptions import FDMSApiException
from .utils import device_id_request, parse_data
from .models.submit_file import SubmitFile, FileStatus


class SubmitFileClient:

    def __init__(self, client):
        self.client = client

    def submit_file(
        self,
        deviceID: int,
        header: dict,
        receipts: list[dict] | None = None,
        footer: dict | None = None,
    ) -> SubmitFileResponse:
        """
        Submit offline device receipts to FDMS as a file.

        This method is asynchronous — FDMS acknowledges the request
        synchronously but processes the file asynchronously.
        Use getFileStatus to check the processing result.

        Can only be used when DeviceOperatingMode is Offline.
        If DeviceOperatingMode is Online, error FILE03 is returned.

        Note: receipts is mandatory when submitting invoices.
        Note: footer is mandatory when submitting a Z report and
              initiating fiscal day closure.
        Note: deviceID in path and header deviceId must match (FILE05).
        Note: Maximum file size is 3 MB (FILE01).
        Note: Zero value counters must not be submitted in footer fiscalDayCounters.

        :param deviceID: Device identification ID. Must match header deviceId.
        :type  deviceID: ``int``

        :param header: File header with device and fiscal day identification.
                       Required keys: deviceId, fiscalDayNo, fiscalDayOpened, fileSequence.
        :type  header: ``dict``

        :param receipts: List of receipt dicts to submit.
                         Mandatory when sending invoices.
                         Each receipt requires: receiptType, receiptCurrency,
                         receiptCounter, receiptGlobalNo, invoiceNo, receiptDate,
                         receiptLinesTaxInclusive, receiptLines, receiptTaxes,
                         receiptPayments, receiptTotal, receiptDeviceSignature.
        :type  receipts: ``list[dict] | None``

        :param footer: File footer with fiscal day counters, device signature
                       and fiscal day closure details.
                       Mandatory when sending Z report.
                       Required keys: fiscalDayCounters, fiscalDayDeviceSignature,
                       receiptCounter, fiscalDayClosed.
        :type  footer: ``dict | None``

        :return: SubmitFileResponse with the operationID assigned by FDMS.
        :rtype:  SubmitFileResponse

        :raises FDMSApiException: If the API returns a DEV or FILE error.
        :raises FDMSValidationException: If receipt validation fails (RCPT0xx).
        """

        payload = {"header": header}

        # Wrap receipts into content structure internally
        if receipts is not None:
            payload["content"] = {"receipts": receipts}

        if footer is not None:
            payload["footer"] = footer

        response = self.client.post(
            f"{deviceID}/SubmitFile",
            payload,
        )
        return parse_data(response, SubmitFile)

    def get_file_status(
        self,
        deviceID: int,
        fileUploadedFrom: str,
        fileUploadedTill: str,
        operationID: str | None = None,
    ) -> FileStatusResponse:
        """
        Get the processing status of a previously submitted file.

        Can only be used when DeviceOperatingMode is Offline.
        The date interval between fileUploadedFrom and fileUploadedTill
        cannot exceed 100 days.

        Request will be rejected if:
            - Fiscal device status is other than Active.
            - Fiscal device operating mode is other than Offline.
            - Request structure is not valid.

        :param deviceID: Device identification ID.
        :type  deviceID: ``int``

        :param fileUploadedFrom: Start date for file upload search range.
                                 Format: "YYYY-MM-DD".
                                 Interval between from and till cannot exceed 100 days.
        :type  fileUploadedFrom: ``str``

        :param fileUploadedTill: End date for file upload search range.
                                 Format: "YYYY-MM-DD".
                                 Interval between from and till cannot exceed 100 days.
        :type  fileUploadedTill: ``str``

        :param operationID: Unique operation ID received in submitFile response.
                            Mandatory if fiscalDayNo is not sent.
        :type  operationID: ``str | None``

        :return: FileStatusResponse with operationID and list of file statuses.
        :rtype:  FileStatusResponse

        :raises FDMSApiException: If the API returns a DEV or FILE error.
        """

        params = {
            "fileUploadedFrom": fileUploadedFrom,
            "fileUploadedTill": fileUploadedTill,
        }

        if operationID is not None:
            params["operationID"] = operationID

        response = self.client.get(
            f"{deviceID}/GetFileStatus",
            params=params,
        )
        return parse_data(response, FileStatus)