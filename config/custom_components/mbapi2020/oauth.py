"""Define an object to interact with the REST API."""
from __future__ import annotations

import asyncio
from copy import deepcopy
import json
import logging
import os
import shutil
import time
import urllib.parse
import uuid

from aiohttp import ClientSession

from custom_components.mbapi2020.errors import MBAuthError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import STORAGE_DIR

from .const import (
    DEFAULT_COUNTRY_CODE,
    DEFAULT_LOCALE,
    REGION_APAC,
    REGION_CHINA,
    REGION_EUROPE,
    REGION_NORAM,
    RIS_APPLICATION_VERSION,
    RIS_APPLICATION_VERSION_CN,
    RIS_APPLICATION_VERSION_NA,
    RIS_APPLICATION_VERSION_PA,
    RIS_OS_NAME,
    RIS_OS_VERSION,
    RIS_SDK_VERSION,
    SYSTEM_PROXY,
    TOKEN_FILE_PREFIX,
    VERIFY_SSL,
    WEBSOCKET_USER_AGENT,
    WEBSOCKET_USER_AGENT_CN,
    WEBSOCKET_USER_AGENT_PA,
    X_APPLICATIONNAME_AP,
    X_APPLICATIONNAME_CN,
    X_APPLICATIONNAME_ECE,
    X_APPLICATIONNAME_US,
)
from .helper import UrlHelper as helper

_LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10


class Oauth:  # pylint: disable-too-few-public-methods
    """define the client."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: ClientSession,
        region: str,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the OAuth instance."""
        self._session: ClientSession = session
        self._region: str = region
        self._hass = hass
        self._config_entry = config_entry
        self._old_token_path = hass.config.path(TOKEN_FILE_PREFIX)
        self._config_entry_token_path: str = None
        if config_entry:
            self._config_entry_token_path = hass.config.path(
                STORAGE_DIR, f"{TOKEN_FILE_PREFIX}-{config_entry.entry_id}"
            )
        self.token = None
        self._xsessionid = ""
        self._get_token_lock = asyncio.Lock()

    async def request_pin(self, email: str, nonce: str):
        """Initiate a PIN request."""
        _LOGGER.info("Start request PIN %s", email)
        _LOGGER.info("PIN preflight request 1")
        headers = self._get_header()
        url = f"{helper.Rest_url(self._region)}/v1/config"
        await self._async_request("get", url, headers=headers)

        _LOGGER.info("PIN request")
        url = f"{helper.Rest_url(self._region)}/v1/login"
        data = f'{{"emailOrPhoneNumber" : "{email}", "countryCode" : "{DEFAULT_COUNTRY_CODE}", "nonce" : "{nonce}"}}'
        headers = self._get_header()
        return await self._async_request("post", url, data=data, headers=headers)

    async def async_refresh_access_token(self, refresh_token: str, is_retry: bool = False):
        """Refresh the access token."""
        _LOGGER.info("Start async_refresh_access_token() with refresh_token")

        _LOGGER.info("Auth token refresh preflight request 1")
        headers = self._get_header()
        url = f"{helper.Rest_url(self._region)}/v1/config"
        await self._async_request("get", url, headers=headers)

        url = f"{helper.Login_Base_Url(self._region)}/as/token.oauth2"
        data = f"grant_type=refresh_token&refresh_token={refresh_token}"

        headers = self._get_header()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["X-Device-Id"] = str(uuid.uuid4())
        headers["X-Request-Id"] = str(uuid.uuid4())
        token_info = None
        try:
            token_info = await self._async_request(method="post", url=url, data=data, headers=headers)

        except MBAuthError as err:
            if is_retry:
                if self._config_entry and self._config_entry.data:
                    new_config_entry_data = deepcopy(dict(self._config_entry.data))
                    new_config_entry_data.pop("token", None)
                    self._hass.config_entries.async_update_entry(self._config_entry, data=new_config_entry_data)
                raise err

        if token_info is not None:
            if "refresh_token" not in token_info:
                token_info["refresh_token"] = refresh_token
            token_info = self._add_custom_values_to_token_info(token_info)
            self._save_token_info(token_info)
            self.token = token_info

        return token_info

    async def request_access_token(self, email: str, pin: str, nonce: str):
        """Request the access token using the Pin."""
        url = f"{helper.Login_Base_Url(self._region)}/as/token.oauth2"
        encoded_email = urllib.parse.quote_plus(email, safe="@")

        data = (
            f"client_id={helper.Login_App_Id(self._region)}&grant_type=password&username={encoded_email}&password={nonce}:{pin}"
            "&scope=openid email phone profile offline_access ciam-uid"
        )

        headers = self._get_header()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Stage"] = "prod"
        headers["X-Device-Id"] = str(uuid.uuid4())
        headers["X-Request-Id"] = str(uuid.uuid4())

        token_info = await self._async_request("post", url, data=data, headers=headers)

        if token_info is not None:
            token_info = self._add_custom_values_to_token_info(token_info)
            if self._config_entry_token_path:
                self._save_token_info(token_info)
            self.token = token_info
            return token_info

        return None

    async def async_get_cached_token(self):
        """Get a cached auth token."""
        _LOGGER.debug("Start async_get_cached_token()")
        token_info: dict[str, any]
        token_type: str = ""

        if self.token:
            token_info = self.token
            token_type = "instance"
        elif not os.path.exists(self._config_entry_token_path):
            if os.path.exists(self._old_token_path):
                _LOGGER.debug("async_get_cached_token: token migration - start copy")
                shutil.copyfile(self._old_token_path, self._config_entry_token_path)
                os.remove(self._old_token_path)

                token_file = open(self._config_entry_token_path)
                token_info_string = token_file.read()
                token_file.close()
                token_info = json.loads(token_info_string)
                token_type = "old_file"
            elif self._config_entry and self._config_entry.data and "token" in self._config_entry.data:
                token_info = self._config_entry.data["token"]
                token_type = "config_entry"
            else:
                _LOGGER.warning("No token information - reauth required")
                return None
        else:
            token_file = open(self._config_entry_token_path)
            token_info_string = token_file.read()
            token_file.close()
            token_info = json.loads(token_info_string)
            token_type = "new_file"

        if self.is_token_expired(token_info):
            async with self._get_token_lock:
                _LOGGER.debug("%s token expired -> start refresh", __name__)
                if not token_info or "refresh_token" not in token_info:
                    _LOGGER.warning("Refresh token is missing - reauth required")
                    return None

                token_info = await self.async_refresh_access_token(token_info["refresh_token"], is_retry=False)

                if not token_info and token_type == "old_file":
                    if os.path.exists(self._old_token_path):
                        _LOGGER.warning("async_get_cached_token: Delete old invalid token file")
                        os.remove(self._old_token_path)
                    if self._config_entry and self._config_entry.data and "token" in self._config_entry.data:
                        token_info = self._config_entry.data["token"]
                        token_type = "config_entry_2"

                        _LOGGER.warning("Starting Refresh token in fallback mode round 2")
                        token_info = await self.async_refresh_access_token(token_info["refresh_token"], is_retry=True)

                    if not token_info:
                        _LOGGER.warning("Refresh token is missing in round 2 - reauth required")
                        return None

        self.token = token_info
        return token_info

    @classmethod
    def is_token_expired(cls, token_info) -> bool:
        """Check if the token is expired."""
        if token_info is not None:
            now = int(time.time())
            return token_info["expires_at"] - now < 60

        return True

    def _save_token_info(self, token_info):
        _LOGGER.debug("Start _save_token_info() to %s", self._config_entry_token_path)

        new_config_entry_data = deepcopy(dict(self._config_entry.data))
        new_config_entry_data["token"] = token_info
        self._hass.config_entries.async_update_entry(self._config_entry, data=new_config_entry_data)

        try:
            with open(self._config_entry_token_path, "w") as token_file:
                token_file.write(json.dumps(token_info))
                token_file.close()
        except OSError:
            _LOGGER.error("Couldn't write token cache to %s", self._config_entry_token_path)
            raise

    @classmethod
    def _add_custom_values_to_token_info(cls, token_info):
        """Store some values that aren't directly provided by a Web API response."""
        token_info["expires_at"] = int(time.time()) + token_info["expires_in"]
        return token_info

    def _get_header(self):
        if not self._xsessionid:
            self._xsessionid = str(uuid.uuid4())

        header = {
            "Ris-Os-Name": RIS_OS_NAME,
            "Ris-Os-Version": RIS_OS_VERSION,
            "Ris-Sdk-Version": RIS_SDK_VERSION,
            "X-Locale": DEFAULT_LOCALE,
            "X-Trackingid": str(uuid.uuid4()),
            "X-Sessionid": self._xsessionid,
            "User-Agent": WEBSOCKET_USER_AGENT,
            "Content-Type": "application/json",
            "Accept-Language": "en-GB",
        }

        header = self._get_region_header(header)

        return header

    def _get_region_header(self, header):
        if self._region == REGION_EUROPE:
            header["X-Applicationname"] = X_APPLICATIONNAME_ECE
            header["Ris-Application-Version"] = RIS_APPLICATION_VERSION

        if self._region == REGION_NORAM:
            header["X-Applicationname"] = X_APPLICATIONNAME_US
            header["Ris-Application-Version"] = RIS_APPLICATION_VERSION_NA

        if self._region == REGION_APAC:
            header["X-Applicationname"] = X_APPLICATIONNAME_AP
            header["Ris-Application-Version"] = RIS_APPLICATION_VERSION_PA
            header["User-Agent"] = WEBSOCKET_USER_AGENT_PA

        if self._region == REGION_CHINA:
            header["X-Applicationname"] = X_APPLICATIONNAME_CN
            header["Ris-Application-Version"] = RIS_APPLICATION_VERSION_CN
            header["User-Agent"] = WEBSOCKET_USER_AGENT_CN

        return header

    async def _async_request(self, method: str, url: str, data: str = "", **kwargs):
        """Make a request against the API."""

        kwargs.setdefault("headers", {})
        kwargs.setdefault("proxy", SYSTEM_PROXY)

        if not self._session or self._session.closed:
            self._session = async_get_clientsession(self._hass, VERIFY_SSL)

        async with self._session.request(method, url, data=data, **kwargs) as resp:
            # _LOGGER.warning("ClientError requesting data from %s: %s", url, resp.json)
            # resp.raise_for_status()

            if 400 <= resp.status < 500:
                try:
                    error = await resp.text()
                    error_json = json.loads(error)
                    if error_json:
                        error_message = f'Error requesting: {url} - {error_json["code"]} - {error_json["errors"]}'
                    else:
                        error_message = f"Error requesting: {url} - 0 - {error}"
                except (json.JSONDecodeError, KeyError):
                    error_message = f"Error requesting: {url} - 0 - {error}"

                _LOGGER.error(error_message)
                raise MBAuthError(error_message)

            return await resp.json(content_type=None)
