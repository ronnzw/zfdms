import dacite
import requests

from datetime import datetime
from requests import Session

from .exceptions import FDMSApiException


def parse_data(data: dict,obj: object) -> object:
    """
    Parse a raw API response into the respective dataclass.
    """
    return dacite.from_dict(
        data_class=obj,
        data=data,
        config=dacite.Config(
            type_hooks={
                datetime: lambda v: datetime.fromisoformat(v) if v else None
            }
        )
    )

def device_id_request(
    _method: str, 
    client: Session, 
    deviceID: int, 
    _endpoint: str
):
    """
    Makes request to endpoint the take deviceID as the only input.

    :param _method: Method for the API endpoint.
    :type  _method: ``str``

    :param client: Initialised session
    :type  client: ``Session``

    :param deviceID: Identifier of the device
    :type  deviceID: ``int``

    :param _endpoint: The endpoint you are trying to request
    :type  _endpoint: ``str``

    :return: response as a dict.
    :rtype: ``dict``
    :raises FDMSApiException: If the API returns an error response.
    """
    try:
        response = client._make_request(
            method=_method.upper(),
            endpoint=f"/Device/v2/{deviceID}/{endPoint}",
            auth_required=True,
        )
        response.raise_for_status()
        data = response.json()
        return data
    except requests.HTTPError as http_err:
        raise FDMSApiException.from_response(http_err.response) from http_err