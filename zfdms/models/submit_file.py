from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class FileStatus:
    """
    Status details for a single previously submitted file.
    """
    operationID: str
    fileUploadDate: str
    deviceId: int
    fileName: str
    fileProcessingStatus: str
    fiscalDayNo: int
    fiscalDayOpenedAt: str
    fileSequence: int
    ipAddress: str
    fileProcessingDate: Optional[str] = None
    fileProcessingErrorCode: list[str] = field(
        default_factory=list
    )


@dataclass
class FileStatus:
    """
    Response returned by FDMS for a getFileStatus request.
    Contains the operation ID and a list of file statuses.
    """
    operationID: str = ""
    fileStatus: list[FileStatus] = field(
        default_factory=list
    )  


@dataclass
class SubmitFile:
    """
    Response returned by FDMS after a file is submitted.
    Processing is asynchronous — use getFileStatus to check the result.
    """
    operationID: str