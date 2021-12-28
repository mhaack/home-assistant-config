"""Define an object to interact with the REST API."""
import json
import logging
import time
import urllib.parse
import uuid
from typing import Optional

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError

from .errors import RequestError
from .const import (
    REGION_EUROPE,
    REGION_NORAM,
    REGION_APAC,
    LOGIN_APP_ID_EU,
    LOGIN_BASE_URI,
    LOGIN_BASE_URI_NA,
    LOGIN_BASE_URI_PA,
    REST_API_BASE,
    REST_API_BASE_NA,
    REST_API_BASE_PA,
    RIS_APPLICATION_VERSION,
    RIS_APPLICATION_VERSION_NA,
    RIS_APPLICATION_VERSION_PA,
    RIS_SDK_VERSION,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10
SYSTEM_PROXY = None
PROXIES = {}
#SYSTEM_PROXY = "http://localhost:8080"
#PROXIES = {
#  'https': SYSTEM_PROXY,
#}

class Oauth: # pylint: disable-too-few-public-methods
    """ define the client. """
    def __init__(
        self,
        *,
        session: Optional[ClientSession] = None,
        locale: Optional[str] = "DE",
        country_code: Optional[str] = "de-DE",
        cache_path: Optional[str] = None,
        region: str = None
    ) -> None:
        self.token = None
        self._locale = locale
        self._country_code = country_code
        self._session: ClientSession = session
        self._region: str = region
        self.cache_path = cache_path


    async def request_pin(self, email: str, nonce: str):
        _LOGGER.info("start request pin %s", email)
        url = f"{REST_API_BASE if self._region == 'Europe' else REST_API_BASE_NA}/v1/login"
        data = f'{{"countryCode":"{self._country_code}","emailOrPhoneNumber":"{email}","locale":"{self._locale}", "nonce":"{ nonce }"}}'
        headers = self._get_header()
        return await self._async_request("post", url, data=data, headers=headers )


    async def async_refresh_access_token(self, refresh_token: str):
        _LOGGER.info("start async refresh_access_token with refresh_token")

       # url = f"{LOGIN_BASE_URI if self._region == 'Europe' else LOGIN_BASE_URI_NA}/auth/realms/Daimler/protocol/openid-connect/token"
       # data = (
       #     f"client_id=app&grant_type=refresh_token&refresh_token={refresh_token}"
       # )

        url = f"{LOGIN_BASE_URI}/as/token.oauth2"
        data = (
            f"client_id=01398c1c-dc45-4b42-882b-9f5ba9f175f1&grant_type=refresh_token&refresh_token={refresh_token}"
        )

        headers = self._get_header()
        headers['Content-Type'] = "application/x-www-form-urlencoded"
        headers['Stage'] = "prod"
        headers['X-AuthMode'] = "CIAMNG"
        headers['device-uuid'] = str(uuid.uuid4())

        token_info = await self._async_request(method="post", url=url, data=data, headers=headers)

        if token_info is not None:
            if "refresh_token" not in token_info:
                token_info["refresh_token"] = refresh_token
            token_info = self._add_custom_values_to_token_info(token_info)
            self._save_token_info(token_info)
            self.token = token_info

        return token_info


    async def request_access_token(self, email: str, pin: str, nonce: str):

        url = f"{LOGIN_BASE_URI}/as/token.oauth2"
        encoded_email = urllib.parse.quote_plus(email, safe='@')
        data = (
            f"client_id=01398c1c-dc45-4b42-882b-9f5ba9f175f1&grant_type=password&username={encoded_email}&password={nonce}:{pin}"
            "&scope=offline_access"
        )


        headers = self._get_header()
        headers['Content-Type'] = "application/x-www-form-urlencoded"
        headers['Stage'] = "prod"
        headers['X-AuthMode'] = "CIAMNG"
        headers['device-uuid'] = str(uuid.uuid4())

        token_info = await self._async_request("post", url, data=data, headers=headers)

        if token_info is not None:
            token_info = self._add_custom_values_to_token_info(token_info)
            self._save_token_info(token_info)
            self.token = token_info
            return token_info

        return None

    async def async_get_cached_token(self):
        """ Gets a cached auth token
        """
        _LOGGER.debug("start: async_get_cached_token")
        token_info = None
        if self.cache_path:
            try:
                token_file = open(self.cache_path)
                token_info_string = token_file.read()
                token_file.close()
                token_info = json.loads(token_info_string)

                if self.is_token_expired(token_info):
                    _LOGGER.debug("%s - token expired - start refresh", __name__)
                    if "refresh_token" not in token_info:
                        _LOGGER.warn("Refresh Token is missing - reauth required")
                        return None
                    token_info = await self.async_refresh_access_token(token_info["refresh_token"])

            except IOError:
                pass
        self.token = token_info
        return token_info

    def is_token_expired(self, token_info):
        if token_info is not None:
            now = int(time.time())
            return token_info["expires_at"] - now < 60
        
        return True

    def _save_token_info(self, token_info):
        _LOGGER.debug("start: _save_token_info to %s", self.cache_path)
        if self.cache_path:
            try:
                token_file = open(self.cache_path, "w")
                token_file.write(json.dumps(token_info))
                token_file.close()
            except IOError:
                _LOGGER.warning("couldn't write token cache to %s", self.cache_path)

    def _add_custom_values_to_token_info(self, token_info):
        """
        Store some values that aren't directly provided by a Web API
        response.
        """
        token_info["expires_at"] = int(time.time()) + token_info["expires_in"]
        # token_info["scope"] = self.OAUTH_SCOPE
        return token_info

    def _get_header(self) -> list:

        header = {
            "X-SessionId": str(uuid.uuid4()),      # "bc667b25-1964-4ff8-98f0-aef3a7f35208",
            "X-TrackingId": str(uuid.uuid4()),     # "abbc223e-bdb8-4808-b299-8ff800b58816",
            "ris-os-name": "android",
            "ris-os-version": "6.0",
            "ris-sdk-version": RIS_SDK_VERSION,
            "X-Locale": self._locale,
            "User-Agent": "okhttp/3.14.9",
            "Content-Type": "application/json; charset=UTF-8"
        }

        header = self._get_region_header(header)

        return header


    def _get_region_header(self, header) -> list:
        
        if self._region == REGION_EUROPE:
            header["X-ApplicationName"] = "mycar-store-ece"
            header["ris-application-version"] = RIS_APPLICATION_VERSION

        if self._region == REGION_NORAM:
            header["X-ApplicationName"] = "mycar-store-us"
            header["ris-application-version"] = RIS_APPLICATION_VERSION_NA

        if self._region == REGION_APAC:
            header["X-ApplicationName"] = "mycar-store-ap"
            header["ris-application-version"] = RIS_APPLICATION_VERSION_PA

        return header

    def _get_restapi_base_url(self) -> str:
        if self._region == REGION_EUROPE:
            return REST_API_BASE

        if self._region == REGION_NORAM:
            return REST_API_BASE_NA

        if self._region == REGION_APAC:
            return REST_API_BASE_PA

    def _get_login_base_url(self) -> str:
        if self._region == REGION_EUROPE:
            return LOGIN_BASE_URI

        if self._region == REGION_NORAM:
            return LOGIN_BASE_URI_NA

        if self._region == REGION_APAC:
            return LOGIN_BASE_URI_PA

    async def _async_request(self, method: str,  url: str, data: str = "", **kwargs) -> list:
        """Make a request against the API."""

        kwargs.setdefault("headers", {})
        kwargs.setdefault("proxy", SYSTEM_PROXY)

        use_running_session = self._session and not self._session.closed

        if use_running_session:
            session = self._session
        else:
            session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))

        try:
            async with session.request(method, url, data=data, **kwargs) as resp:
                resp.raise_for_status()
                return await resp.json(content_type=None)
        except ClientError as err:
            _LOGGER.error(f"Error requesting data from {url}: {err}")
        except Exception as e:
            _LOGGER.error(f"Error requesting data from {url}: {e}")
        finally:
            if not use_running_session:
                await session.close()
