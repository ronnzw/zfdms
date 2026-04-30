from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DeviceOperatingMode(str, Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"


@dataclass
class FiscalDayServerSignature:
    """Signature for the fiscal day"""
    certificateThumbprint = ""
    hash = ""
    signature = ""


@dataclass
class FiscalDay:
    """Fiscal Day"""
    operationID: str = ""
    fiscalDayStatus: str = ""
    fiscalDayReconciliationMode: str = ""
    fiscalDayServerSignature: FiscalDayServerSignature = field(default_factory=FiscalDayServerSignature)
    fiscalDayClosed: datetime = None
    lastFiscalDayNo: int = 0
    lastReceiptGlobalNo: int = 0
