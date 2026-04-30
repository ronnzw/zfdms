from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ReceiptServerSignature:
    """FDMS generated signature confirming receipt was accepted."""
    certificateThumbprint: str = ""
    hash: str = ""
    signature: str = ""

@dataclass
class SubmitReceipt:
    """Response returned by FDMS after a receipt is submitted."""
    receiptID: int = 0
    serverDate: Optional[datetime] = None
    receiptServerSignature: ReceiptServerSignature = field(
        default_factory=ReceiptServerSignature
    )
    operationID: str = ""
