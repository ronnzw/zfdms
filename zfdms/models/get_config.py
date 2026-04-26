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
    operationID: str = ""
    taxPayerName: str = ""
    taxPayerTIN: str = ""
    deviceSerialNo: str = ""
    deviceBranchName: str = ""
    deviceBranchAddress: Address = field(default_factory=Address)
    deviceOperatingMode: DeviceOperatingMode = DeviceOperatingMode.ONLINE
    taxPayerDayMaxHrs: int = 0
    taxpayerDayEndNotificationHrs: int = 0
    applicableTaxes: list[Tax] = field(default_factory=list)
    certificateValidTill: datetime | None = None
    qrUrl: str = ""
    vatNumber: str | None = None
    deviceBranchContacts: Contacts | None = None


# ── Factory / Deserializer ────────────────────────────────────────────────────

# def parse_device_config(data: dict) -> DeviceConfig:
#     """
#     Parse a raw API response dict into a DeviceConfig dataclass.
#     Handles nested objects, optional fields, and datetime parsing.
#     """
#     return dacite.from_dict(
#         data_class=DeviceConfig,
#         data=data,
#         config=dacite.Config(
#             type_hooks={
#                 datetime: lambda v: datetime.fromisoformat(v) if v else None,
#                 DeviceOperatingMode: DeviceOperatingMode,
#             },
#             cast=[DeviceOperatingMode],
#         )
#     )

