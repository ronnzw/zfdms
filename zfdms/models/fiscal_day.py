from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DeviceOperatingMode(str, Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"


@dataclass
class FiscalDayServerSignature:
    """Signature for the fiscal day"""
    certificateThumbprint: str = ""
    hash: str = ""
    signature: str = ""


@dataclass
class FiscalDay:
    """Fiscal Day"""
    operationID: str
    fiscalDayStatus: str
    fiscalDayReconciliationMode: str
    fiscalDayServerSignature: FiscalDayServerSignature =field(default_factory=FiscalDayServerSignature)
    fiscalDayClosed: datetime | None = None
    lastFiscalDayNo: int = 0
    lastReceiptGlobalNo: int = 0


@dataclass
class FiscalDayOpen:
    fiscalDayNo: int = 0
    fiscalDayOpened: datetime | None = None


@dataclass
class FiscalDayCounter:
    fiscalCounterType: str = "",
    fiscalCounterCurrency: str = "",
    fiscalCounterTaxPercent: int = 0,
    fiscalCounterTaxID: int = 0,
    fiscalCounterMoneyType: str = "",
    fiscalCounterValue: int = 0


@dataclass
class FiscalDayClose:
    fiscalDayNo: int = 0
    fiscalDayCounters: FiscalDayCounter = field(default_factory=FiscalDayCounter)
    fiscalDayDeviceSignature: FiscalDayServerSignature = field(default_factory=FiscalDayServerSignature)
    receiptCounter: int = 0

