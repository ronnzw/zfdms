from typing import Optional
from dacite import from_dict


HTTP_STATUS_DESCRIPTIONS = {
    400: "Bad request – the message is malformed and could not be processed.",
    401: "Authentication error – certificate invalid, revoked, expired, or not issued to this device.",
    404: "Resource not found – call to a non-existing endpoint.",
    405: "Method not allowed – unsupported HTTP method used for this endpoint.",
    422: "Unprocessable content – instructions given by fiscal device are incorrect.",
    500: "Infrastructure error – Fiscal Backend Gateway unavailable. Retry later.",
    502: "Bad gateway – Fiscal Backend Gateway could not be contacted. Retry later.",
}

FDMS_ERROR_CODES = {
    # Device errors
    "DEV01": "Device not found or not active.",
    "DEV02": "Activation key is incorrect.",
    "DEV03": "Certificate request is invalid.",
    "DEV04": "Device model is blacklisted.",
    "DEV05": "Taxpayer is not active.",
    "DEV06": "Device model and version is not registered in FDMS.",
    "DEV07": "Username is already used.",
    "DEV08": "Provided user information is not correct.",
    "DEV09": "Security code is not valid.",
    "DEV10": "Password is not valid.",
    "DEV11": "User credentials are incorrect.",
    "DEV12": "Token is not valid.",
    "DEV13": "User is not confirmed.",
    "DEV14": "Email or phone number is not valid or doesn't exist.",
    "DEV15": "Email or phone number already confirmed.",
    # Receipt errors
    "RCPT01": "Submitting receipt is not allowed. Fiscal day is closed or fiscal day close initiated.",
    "RCPT02": "Submit receipt failed. The receipt structure is invalid or field requirements not satisfied.",
    # Fiscal day errors
    "FISC01": "Open day is not allowed.",
    "FISC03": "Closing day is not allowed. Close day is in progress.",
    "FISC04": "Closing day is not allowed. Fiscal day not opened.",
    # File errors
    "FILE01": "File is too big. Allowed file size: 3 MB.",
    "FILE02": "File structure invalid or field requirements not satisfied.",
    "FILE03": "Device operating mode is not Offline.",
    "FILE04": "File sent for already closed day or closing in progress.",
    "FILE05": "Device ID in input parameters and file header are different.",
}


class ValidationColor:
    RED = "Red"
    YELLOW = "Yellow"
    GREY = "Grey"


RECEIPT_VALIDATION_ERRORS = {
    "RCPT010": (ValidationColor.RED,    False, "Wrong currency code is used."),
    "RCPT011": (ValidationColor.RED,    True,  "Receipt counter is not sequential."),
    "RCPT012": (ValidationColor.RED,    True,  "Receipt global number is not sequential."),
    "RCPT013": (ValidationColor.RED,    False, "Invoice number is not unique."),
    "RCPT014": (ValidationColor.YELLOW, False, "Receipt date is earlier than fiscal day opening date."),
    "RCPT015": (ValidationColor.RED,    False, "Credited/debited invoice data is not provided."),
    "RCPT016": (ValidationColor.RED,    False, "No receipt lines provided."),
    "RCPT017": (ValidationColor.RED,    False, "Taxes information is not provided."),
    "RCPT018": (ValidationColor.RED,    False, "Payment information is not provided."),
    "RCPT019": (ValidationColor.RED,    False, "Invoice total amount is not equal to sum of all invoice lines."),
    "RCPT020": (ValidationColor.RED,    False, "Invoice signature is not valid."),
    "RCPT021": (ValidationColor.RED,    False, "VAT tax is used in invoice while taxpayer is not VAT taxpayer."),
    "RCPT022": (ValidationColor.RED,    False, "Invoice sales line price must be greater than 0 (less than 0 for Credit note)."),
    "RCPT023": (ValidationColor.RED,    False, "Invoice line quantity must be positive."),
    "RCPT024": (ValidationColor.RED,    False, "Invoice line total is not equal to unit price * quantity."),
    "RCPT025": (ValidationColor.RED,    False, "Invalid tax is used."),
    "RCPT026": (ValidationColor.RED,    False, "Incorrectly calculated tax amount."),
    "RCPT027": (ValidationColor.RED,    False, "Incorrectly calculated total sales amount (including tax)."),
    "RCPT028": (ValidationColor.RED,    False, "Payment amount must be greater than or equal to 0 (less than or equal to 0 for Credit note)."),
    "RCPT029": (ValidationColor.RED,    False, "Credited/debited invoice information provided for regular invoice."),
    "RCPT030": (ValidationColor.RED,    True,  "Invoice date is earlier than previously submitted receipt date."),
    "RCPT031": (ValidationColor.YELLOW, False, "Invoice is submitted with a future date."),
    "RCPT032": (ValidationColor.RED,    False, "Credit/debit note refers to non-existing invoice."),
    "RCPT033": (ValidationColor.RED,    False, "Credited/debited invoice is issued more than 12 months ago."),
    "RCPT034": (ValidationColor.RED,    False, "Note for credit/debit note is not provided."),
    "RCPT035": (ValidationColor.RED,    False, "Total credit note amount exceeds original invoice amount."),
    "RCPT036": (ValidationColor.RED,    False, "Credit/debit note uses other taxes than are used in the original invoice."),
    "RCPT037": (ValidationColor.RED,    False, "Invoice total amount is not equal to sum of all invoice lines and taxes applied."),
    "RCPT038": (ValidationColor.RED,    False, "Invoice total amount is not equal to sum of sales amount including tax in tax table."),
    "RCPT039": (ValidationColor.RED,    False, "Invoice total amount is not equal to sum of all payment amounts."),
    "RCPT040": (ValidationColor.RED,    False, "Invoice total amount must be greater than or equal to 0 (less than or equal to 0 for Credit note)."),
    "RCPT041": (ValidationColor.YELLOW, False, "Invoice is issued after fiscal day end."),
    "RCPT042": (ValidationColor.RED,    False, "Credit/debit note uses other currency than is used in the original invoice."),
    "RCPT043": (ValidationColor.RED,    False, "Mandatory buyer data fields are not provided."),
    "RCPT047": (ValidationColor.RED,    False, "HS code must be sent if taxpayer is a VAT payer."),
    "RCPT048": (ValidationColor.RED,    False, "HS code length must be 4 or 8 digits."),
}


def get_validation_error_info(code: str):
    """
    Returns (color, requires_previous_receipt, description) for a validation error code,
    or None if the code is not recognised.
    """
    return RECEIPT_VALIDATION_ERRORS.get(code)



class FDMSApiException(Exception):
    """
    Raised when the FDMS API returns a 4xx or 5xx HTTP error.

    The response body follows RFC 7807 Problem Details:
        type        - URI reference identifying the problem
        title       - Human-readable problem summary
        status      - HTTP status code
        errorCode   - FDMS-specific error code (optional)

    Retryable statuses (device should retry later): 500, 502
    """

    #: HTTP status codes where the device should retry the request later
    RETRYABLE_STATUSES = {500, 502}

    def __init__(
        self,
        status_code: int,
        message: str,
        uri: Optional[str] = None,
        error_code: Optional[str] = None,
        title: Optional[str] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.uri = uri
        self.error_code = error_code
        self.title = title
        self.error_description = FDMS_ERROR_CODES.get(error_code) if error_code else None
        self.status_description = HTTP_STATUS_DESCRIPTIONS.get(status_code)
        self.should_retry = status_code in self.RETRYABLE_STATUSES

    def __str__(self):
        parts = [f"FDMS API Error [{self.status_code}]"]

        if self.uri:
            parts.append(f"on '{self.uri}'")

        if self.error_code:
            parts.append(f"- {self.error_code}")

        if self.error_description:
            parts.append(f": {self.error_description}")
        elif self.title:
            parts.append(f": {self.title}")
        else:
            parts.append(f": {self.message}")

        if self.should_retry:
            parts.append("(retryable)")

        return " ".join(parts)


class FDMSValidationException(FDMSApiException):
    """
    Raised specifically for receipt validation errors (RCPT0xx codes).

    Validation errors are categorised by color:
        Red    - Major error. Fiscal day cannot be closed automatically.
        Yellow - Minor error. Fiscal day can still be closed automatically.
        Grey   - Receipt chain gap. Revalidated when previous receipt is received.
                 Fiscal day cannot be closed automatically if any Grey receipts exist.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        uri: Optional[str] = None,
        error_code: Optional[str] = None,
        title: Optional[str] = None,
    ):
        super().__init__(status_code, message, uri, error_code, title)

        info = get_validation_error_info(error_code) if error_code else None
        if info:
            self.color, self.requires_previous_receipt, self.validation_description = info
        else:
            self.color = None
            self.requires_previous_receipt = False
            self.validation_description = None

    def __str__(self):
        base = super().__str__()
        if self.color:
            return f"{base} [Severity: {self.color}]"
        return base