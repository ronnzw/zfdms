from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DeviceOperatingMode(str, Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"


@dataclass
class Address:
    """Device branch address."""
    province: str = ""
    street: str = ""
    houseNo: str = ""
    city: str = ""


@dataclass
class Contacts:
    """Device branch contact information (optional)."""
    phoneNo: str = ""
    email: str = ""


@dataclass
class Tax:
    """
    Applicable tax rate.
    taxPercent is absent for exempt taxes.
    """
    taxName: str = ""
    taxPercent: float | None = None


@dataclass
class DeviceConfig:
    operationID: str
    taxPayerName: str
    taxPayerTIN: str
    deviceSerialNo: str
    deviceBranchName: str
    deviceBranchAddress: Address = field(default_factory=Address)
    deviceOperatingMode: DeviceOperatingMode = DeviceOperatingMode
    taxPayerDayMaxHrs: int = 0
    taxpayerDayEndNotificationHrs: int = 0
    applicableTaxes: list[Tax] = field(default_factory=list)
    certificateValidTill: datetime | None = None
    qrUrl: str = ''
    vatNumber: str | None = None
    deviceBranchContacts: Contacts | None = None