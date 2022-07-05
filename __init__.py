"""
Python API wrapper for Garmin Connect to grab data and statistics
"""

import json
import logging
import re
import requests
import cloudscraper


from enum import Enum, auto
from typing import Any, Dict


logger = logging.getLogger(__name__)


class ApiClient:
    """
    Class for a single API endpoint
    """

    default_headers = {
        # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.121 Safari/535.2"
        "User-Agent": "Mozilla/5.0 (Macinthosh; Intel Mac OS X 10.14, rv:66.0) Gecko/20100101 Firefox/66.0"
    }


    def set_cookies(self, cookies):
        logger.debug('Restoring cookies for saved session.')
        self.session.cookies.update(cookies)

    
    def get_cookies(self):
        return self.session.cookies


    def clear_cookies(self):
        self.session.cookies.clear()


    def url(self, add_url=None):
        """
        
        """

        path = f"https://{self.base_url}"
        if add_url is not None:
            path += f"/{add_url}"
        
        return path


    def get(self, add_url, additional_headers=None, params=None):
        """
        """

        total_headers = self.headers.copy()
        if additional_headers:
            total_headers.update(additional_headers)
        url = self.url(add_url)

        logger.debug("URL: %s", url)
        logger.debug("headers: %s", total_headers)

        try:
            response = self.session.get(url, headers=total_headers, params=params)
            response.raise_for_status()
            # logger.debug("Response: %s", response.content)
            return response
        except Exception as err:
            logger.debug("Response in exception: %s", response.content)
            if response.status_code == 429:
                raise GarminConnectTooManyRequestsError(f"Too many requests: {err}") from err
            if response.status_code == 401:
                raise GarminConnectAuthenticationError(f"Authentication error: {err}") from err
            if response.status_code == 403:
                raise GarminConnectConnectionError(f"Forbidden URL: {url}") from err

            raise GarminConnectConnectionError(err) from err

    def post(self, add_url, additional_headers, params, data):
        """
        """

        total_headers = self.headers.copy()
        if additional_headers:
            total_headers.update(additional_headers)
        url = self.url(add_url)

        logger.debug("URL: %s", url)
        logger.debug("Headers: %s", total_headers)
        logger.debug("Data: %s", data)

        try:
            response = self.session.post(url, headers=total_headers, params=params, data=data)
            response.raise_for_status()
            # logger.debug("Response: %s", response.content)
            return response
        except Exception as err:
            logger.debug("Response in exception: %s", response.content)
            if response.status_code == 429:
                raise GarminConnectTooManyRequestsError(f"Too many requests: {err}") from err
            if response.status_code == 401:
                raise GarminConnectAuthenticationError(f"Authentication error: {err}") from err
            if response.status_code == 403:
                raise GarminConnectConnectionError(f"Forbidden URL: {url}") from err

            raise GarminConnectConnectionError(err) from err


    def __init__(self, session, base_url, headers=None, additional_headers=None):
        """
        """
        
        self.session = session
        self.base_url = base_url

        if headers:
            self.headers = headers

        else:
            self.headers = self.default_headers.copy()

        if additional_headers:
            self.headers.update(additional_headers)


class Garmin:
    """
    """

    def __init__(self, email, password, is_cn=False, session_data=None):
        """
        
        """

        self.session_data = session_data

        self.username = email
        self.is_cn = is_cn

        self.garmin_connect_base_url = "https://connect.garmin.com"
        self.garmin_connect_sso_url = "sso.garmin.com/sso"
        self.garmin_connect_modern_url = "connect.garmin.com/modern"
        self.garmin_connect_css_url = "https://static.garmincdn.com/com.garmin.connect/ui/css/gauth-custom-v1.2-min.css"

        if self.is_cn:
            self.garmin_connect_base_url = "https://connect.garmin.cn"
            self.garmin_connect_sso_url = "sso.garmin.cn/sso"
            self.garmin_connect_modern_url = "connect.garmin.cn/modern"
            self.garmin_connect_css_url = "https://static.garmincdn.cn/cn.garmin.connect/ui/css/gauth-custom-v1.2-min.css"

        self.garmin_connect_login_url = self.garmin_connect_base_url + "/en-US/signin"
        self.garmin_connect_sso_login = "signin"

        self.garmin_connect_devices_url = "proxy/device-service/deviceregistration/devices"
        self.garmin_connect_device_url = "proxy/device-service/deviceservice"
        self.garmin_connect_weight_url = "proxy/weight-service/weight/dateRange"
        self.garmin_connect_daily_summary_url = "proxy/usersummary-service/usersummary/daily"
        self.garmin_connect_metrics_url = "proxy/metrics-service/metrics/maxmet/daily"
        self.garmin_connect_daily_hydration_url = "proxy/usersummary-service/usersummary/hydration/daily"
        self.garmin_connect_personal_record_url = "proxy/personalrecord-service/personalrecord/prs"
        self.garmin_connect_earned_badges_url = "proxy/badge-service/badge/earned"
        self.garmin_connect_adhoc_challenges_url = "proxy/adhocchallenge-service/adHocChallenge/historical"
        self.garmin_connect_badge_challenges_url = "proxy/badgechallenge-service/badgeChallenge/completed"
        self.garmin_connect_daily_sleep_url = "proxy/wellness-service/wellness/dailySleepData"
        self.garmin_connect_daily_stress_url = "proxy/wellness-service/wellness/dailyStress"

        self.garmin_connect_rhr = "proxy/userstats-service/wellness/daily"

        self.garmin_connect_user_summary_chart = "proxy/wellness-service/wellness/dailySummaryChart"
        self.garmin_connect_heartrates_daily_url = "proxy/wellness-service/wellness/dailyHeartRate"
        self.garmin_connect_daily_respiration_url = "proxy/wellness-service/wellness/daily/respiration"
        self.garmin_connect_daily_spo2_url = "proxy/wellness-service/wellness/daily/spo2"
        self.garmin_connect_activities = "proxy/activitylist-service/activities/search/activities"
        self.garmin_connect_activity = "proxy/activity-service/activity"

        self.garmin_connect_fit_download = "proxy/download-service/files/activity"
        self.garmin_connect_tcx_download = "proxy/download-service/export/tcx/activity"
        self.garmin_connect_gpx_download = "proxy/download-service/export/gpx/activity"
        self.garmin_connect_kml_download = "proxy/download-service/export/kml/activity"
        self.garmin_connect_csv_download = "proxy/download-service/export/csv/activity"
        self.garmin_connect_gear = "proxy/gear-service/gear/filterGear"


        self.garmin_connect_logout = "auth/logout/?url="

        self.garmin_headers = {
            "NK": "NT"
        }

        self.session = cloudscraper.CloudScraper()

        self.sso_rest_client = ApiClient(self.session, self.garmin_connect_sso_url, additional_headers=self.garmin_headers)
        self.modern_rest_client = ApiClient(self.session, self.garmin_connect_modern_url, additional_headers=self.garmin_headers)

        self.display_name = None
        self.full_name = None
        self.unit_system = None

    @staticmethod
    def __get_json(page_html, key):
        """
        """

        found = re.search(key + r" = (\{.*\});", page_html. re.M)
        if found:
            json_text = found.group(1).replace('\\"', '"')
            return json.loads(json_text)

        return None

    def login(self):
        if (self.session_data is None):
            return self.authenticate()
        else:
            return self.login_session()

    
    def login_session(self):
        logger.debug("Login with cookies.")

        session_display_name = self.session_data['display_name']
        logger.debug('Set cookies in session')
        self.modern_rest_client.set_cookies(requests.utils.cookiejar_from_dict(self.session_data['session_cookies']))
        self.sso_rest_client.set_cookies(requests.utils.cookiejar_from_dict(self.session_data['login_cookies']))

        logger.debug("Get page data with cookies.")
        params = {
            "service": "https://connect.garmin.com/modern/",
            "webhost": "https://connect.garmin.com",
            "gateway": "true",
            "generateExtraServiceTicket": "true",
            "generateTwoExtraServiceTickets": "true"
        }

        response = self.sso_rest_client.get("login", params=params)
        logger.debug("Session response %s", response.status_code)
        if response.status_code != 200:
            logger.debug("Session expired, autenticating again.")
            return self.authenticate()

        user_preferences = self.__get_json(response.text, "VIEWER_USERPREDERENCES")
        if (user_preferences is None):
            logger.debug("Session expired, authenticating again.")
            return self.authenticate()

        self.display_name = user_preferences["displayName"]
        logger.debug("Display name is %s", self.display_name)

        self.unit_system = user_preferences["measurementSystem"]
        logger.debug("Unit system is %s", self.unit_system)

        social_profile = self.__get_json(response.text, "VIEWER_SOCIAL_PROFILE")
        self.full_name = social_profile["fullName"]
        logger.debug("Fullname is %s", self.full_name)

        if self.display_name == session_display_name:
            return True
        else:
            logger.debug('Session not valid for user %s', self.display_name)
            return self.authenticate()


    def authenticate(self):
        # TODO add better description
        """
        Login to Garmin Connect.
        """

        logger.debug("Login: %s %s", self.username, self.password)
        self.modern_rest_client.clear_cookies()
        self.sso_rest_client.clear_cookies()

        get_headers = {
            "Referer": self.garmin_connect_login_url
        }
        params = {
            "service": self.modern_rest_client.url(),
            "webhost": self.garmin_connect_base_url,
            "source": self.garmin_connect_login_url,
            "redirectAfterAccountLoginUrl": self.modern_rest_client.url(),
            "redirectAfterAccountCreationUrl": self.modern_rest_client.url(),
            "gauthHost": self.sso_rest_client.url(),
            "locale": "en_US",
            "id": "gauth-widget",
            "cssUrl": self.garmin_connect_css_url,
            "privacyStatementUrl": "//connect.garmin.com/en-US/privacy/",
            "clientId": "GarminConnect",
            "rememberMeShown": "true",
            "rememberMeChecked": "false",
            "createAccountShown": "true",
            "openCreateAccount": "false",
            "displayNameShown": "false",
            "consumeServiceTicket": "false",
            "initialFocus": "true",
            "embedWidget": "false",
            "generateExtraServiceTicket": "true",
            "generateTwoExtraServiceTickets": "false",
            "generateNoServiceTicket": "false",
            "globalOptInShown": "true",
            "globalOptInChecked": "false",
            "mobile": "false",
            "connectLegalTerms": "true",
            "locationPromptShown": "true",
            "showPassword": "true"
        }

        if self.is_cn:
            params["cssUrl"] = "https://static.garmincdn.cn/cn.garmin.connect/ui/css/gauth-custom-v1.2-min.css"

        response = self.sso_rest_client.get(self.garmin_connect_sso_login, get_headers, params)

        found = re.search(r"name=\"_csrf\" value=\"(\w*)", response.text, re.M)
        if not found:
            logger.error("_csrf not found (%d)", response.status_code)
            return False

        csrf = found.group(1)
        referer = response.url
        logger.debug("_csrf found: %s", csrf)
        logger.debug("Referer: %s", referer)

        data = {
            "username": self.username,
            "password": self.password,
            "embed": "false",
            "_csrf": csrf
        }
        
        post_headers = {
            "Referer": referer,
            "Content Type": "application/x-www-form-urlencoded"
        }

        response = self.sso_rest_client.post(self.garmin_connect_sso_login, post_headers, params, data)
        found = re.search(r"\?ticket=([\w-]*)", response.text, re.M)
        if not found:
            logger.error("Login ticket not found (%d).", response.status_code)
            return False
        
        params = {
            "ticket": found.group(1)
        }

        response = self.modern_rest_client.get("", params=params)

        user_preferences = self.__get_json(response.text, "VIEWER_USERPREFERENCES"
        self.display_name = user_preferences["displayName"])
        logger.debug("Display name is %s", self.display_name)

        self.unit_system = user_preferences["measurementSystem"]
        logger.debug("Unit system is %s", self.unit_system)

        social_profile = self.__get_json(response.text, "VIEWER_SOCIAL_PROFILE")
        self.full_name = social_profile["fullName"]
        logger.debug("Fullname is %s", self.full_name)

        self.session_data = {
            'display_name': self.display_name,
            'session_cookies': requests.utils.dict_from_cookiejar(self.modern_rest_client.get_cookies()),
            'login_cookies': requests.utils.dict_from_cookiejar(self.sso_rest_client.get_cookies())
        }

        return True

    def get_full_name(self):
        """
        
        """

        return self.full_name


    def get_unit_system(self):
        """
        """

        return self.unit_system






class GarminConnectConnectionError(Exception):
    # TODO add description
    """
    
    Raised when communication to Garmin Connect failed. 
    """


class GarminConnectTooManyRequestsError(Exception):
    """
    """


class GarminConnectAuthenticationError(Exception):
    """
    """
