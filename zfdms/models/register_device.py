from attr import attrs, attrib


@attrs
class User(object):
    deviceID = attrib(type=int)
    activationKey = attrib(type=str)
    deviceSerialNo = attrib(type=str)
    operationID = attrib(type=str)
    taxPayerName = attrib(type=str)
    taxPayerTIN = attrib(type=str)
    vatNumber = attrib(type=str, default=None)
    deviceBranchName = attrib(type=str)
    deviceBranchAddress = attrib(type=str)
    deviceBranchContact = attrib(type=str)
