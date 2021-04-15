"""Model and Manager for Event resources."""
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Union

import requests

from podman import api
from podman.api.client import APIClient
from podman.errors import APIError

logger = logging.getLogger("podman.events")


class EventsManager:  # pylint: disable=too-few-public-methods
    """Specialized Manager for Event resources."""

    def __init__(self, client: APIClient) -> None:
        """Initiate EventManager object.

        Args:
            client: Connection to Podman service.
        """
        self.client = client

    def list(
        self,
        since: Union[datetime, int, None] = None,
        until: Union[datetime, int, None] = None,
        filters: Optional[Dict[str, Any]] = None,
        decode: bool = False,
    ):
        """Report on networks.

        Args:
            decode: When True, decode stream into dict's. Default: False
            filters: Criteria for including events.
            since: Get events newer than this time.
            until: Get events older than this time.

        Yields:
            When decode is True, Iterator[Dict[str, Any]]
            When decode is False, Iterator[str]
        """
        params = {
            "filters": api.prepare_filters(filters),
            "since": api.prepare_timestamp(since),
            "stream": True,
            "until": api.prepare_timestamp(until),
        }
        response = self.client.get("/events", params=params, stream=True)
        if response.status_code != requests.codes.okay:
            body = response.json()
            raise APIError(body["cause"], response=response, explanation=body["message"])

        for item in response.iter_lines():
            if decode:
                yield json.loads(item)
            else:
                yield item
