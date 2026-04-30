from dataclass import dataclass
from datetime import datetime


@dataclass
class RenewCertificate:
    operationID: str
    certificate: str

@dataclass
class ServerCerts:
    certificate: str
    certificateValidTill: datetime

@dataclass
class PingResponse:
    operationID: str
    reportingFrequency: int