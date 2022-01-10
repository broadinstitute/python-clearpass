# -*- coding: utf-8 -*-
"""Define the clearpass.client.Client class."""

import logging
import sys

import requests

from . import __version__

LOGGER = logging.getLogger(__name__)


class Client(object):
    """Serve as a Base class for calls to the ClearPass APIs."""

    # pylint:disable=too-many-arguments
    def __init__(self, base_url, client_id, client_secret, username, password, grant_type="client_credentials"):
        """Initialize the class.

        Args:
            base_url(string): The full URL to the ClearPass server
            grant_type(string): The OAuth grant type to use
            client_id(string): The OAuth Client ID obtained from ClearPass
            client_secret(string): The OAuth Client Secret obtained from ClearPass
            username(string): The username with which to login
            password(string): The password with which to login
        """
        self.__base_url = base_url
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__username = username
        self.__password = password
        self.__grant_type = grant_type

        self.__session = requests.Session()

        # Set the default HTTP headers
        self.__headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
        }
        self.__session.headers.update(self.__headers)
        self.__access_token = self._get_token()
        self.add_headers({"Authorization": f"Bearer {self.__access_token}"})

    @property
    def user_agent(self):
        """Return a user-agent string including the module version and Python version."""
        ver_info = list(map(str, sys.version_info))
        pyver = ".".join(ver_info[:3])
        useragent = f"{__version__.__title__}/{__version__.__version__} (Python {pyver})"

        return useragent

    @property
    def access_token(self):
        """Return the access token received from ClearPass."""
        return self.__access_token

    @property
    def base_url(self):
        """Return the internal __base_url value."""
        return self.__base_url

    @property
    def client_id(self):
        """Return the internal __base_url value."""
        return self.__client_id

    @property
    def headers(self):
        """Return the internal __headers value."""
        return self.__headers

    @property
    def session(self):
        """Return the setup internal __session requests.Session object."""
        return self.__session

    @property
    def username(self):
        """Return the internal __base_url value."""
        return self.__username

    def _get_token(self):
        """Retrieve an OAuth access token.

        Returns:
            A string representing the ClearPass access token
        """
        data = {
            "grant_type": self.__grant_type,
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "username": self.__username,
            "password": self.__password,
        }

        url = self._url("/oauth")
        result = self.__session.post(url, json=data, headers=self.__headers)
        # Raise an exception if the return code is in an error range
        result.raise_for_status()

        token = result.json()
        if "access_token" not in token:
            raise ClearPassInvalidToken()

        return token["access_token"]

    def _url(self, path):
        """Build the endpoint URL based on the API URL inside this object.

        Args:
            path(string): The path of the URL you wish to create i.e. for
            https://cppm.example.com/api/api-client the path would be /api-client
        Returns:
            A string with the full URL
        """
        url = self.__base_url.rstrip("/")
        url += "/" + "api"
        url += "/" + path.strip("/")

        return url

    def add_headers(self, headers=None):
        """Add the provided headers to the internally stored headers.

        Note: This function will overwrite an existing header if the key in the headers parameter matches one
        of the keys in the internal dictionary of headers.

        Args:
            headers(dict): A dictionary where key is the header with its value being the setting for that header.
        """
        if headers:
            head = self.__headers.copy()
            head.update(headers)
            self.__headers = head
            self.__session.headers.update(self.__headers)

    def remove_headers(self, headers=None):
        """Remove the requested header keys from the internally stored headers.

        Note: If any of the headers in provided the list do not exist, the header will be ignored and will not raise
        an exception.

        :param list headers: A list of header keys to delete
        """
        if headers:
            for head in headers:
                if head in self.__headers:
                    del self.__headers[head]
                    del self.__session.headers[head]

    def get(self, url, headers=None, params=None):
        """Submit a GET request to the provided URL.

        :param str url: A URL to query
        :param dict headers: A dictionary with any extra headers to add to the request
        :param dict params: A dictionary with any parameters to add to the request URL
        :return obj: A requests.Response object received as a response
        """
        full_url = self._url(url)
        result = self.__session.get(full_url, headers=headers, params=params)
        # Raise an exception if the return code is in an error range
        result.raise_for_status()

        return result

    def post(self, url, headers=None, data=None):
        """Submit a POST request to the provided URL and data.

        :param str url: A URL to query
        :param dict headers: A dictionary with any extra headers to add to the request
        :param dict data: A dictionary with the data to use for the body of the POST
        :return obj: A requests.Response object received as a response
        """
        full_url = self._url(url)
        result = self.__session.post(full_url, json=data, headers=headers)
        # Raise an exception if the return code is in an error range
        result.raise_for_status()

        return result

    def put(self, url, headers=None, data=None):
        """Submit a PUT request to the provided URL and data.

        :param str url: A URL to query
        :param dict headers: A dictionary with any extra headers to add to the request
        :param dict data: A dictionary with the data to use for the body of the PUT
        :return obj: A requests.Response object received as a response
        """
        full_url = self._url(url)
        result = self.__session.put(full_url, json=data, headers=headers)
        # Raise an exception if the return code is in an error range
        result.raise_for_status()

        return result

    def delete(self, url, headers=None):
        """Submit a DELETE request to the provided URL.

        :param str url: A URL to query
        :param dict headers: A dictionary with any extra headers to add to the request
        :return obj: A requests.Response object received as a response
        """
        full_url = self._url(url)
        result = self.__session.delete(full_url, headers=headers)
        # Raise an exception if the return code is in an error range
        result.raise_for_status()

        return result


class ClearPassInvalidToken(BaseException):
    """Access token is invalid"""
