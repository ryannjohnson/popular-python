from gettext import gettext as _
import requests

from .base import Provider
from ..exceptions import SocialError, SocialProviderError
from ..users import User


class GoogleProvider(Provider):
    """Provider for github.com authentication."""

    CONFIG_KEYS = [
        'client_id',
        'client_secret',
        'redirect_uri',
    ]

    def get_auth_url(self, state):
        """Generates the url for the user to grant permission on.

        Args:
            state: a string of random characters to help prevent CSRF
                attacks.

        Returns:
            A string URL.
        """
        url = 'https://accounts.google.com/o/oauth2/v2/auth'
        return self.serialize_url(url=url, params=dict(
            client_id=self.config['client_id'],
            redirect_uri=self.config['redirect_uri'],
            scope=' '.join([
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
            ]),
            state=state,
            access_type='online',
            response_type='code',
        ))

    def get_user(self, uri, state):
        """Takes the response URI and retrieves a user from it.

        Args:
            uri: a string uri that the service sent the user to,
                including all query paramters attached.
            state: a string that was provided for this exact request
                when the user was first redirected.

        Returns:
            A popular.users.User instance.

        Raises:
            The state parameter is invalid.
        """
        # See if the uri has what we expect.
        uri_params = self.parse_uri(uri, required=['code', 'state'])
        if state:
            if uri_params['state'] != state:
                raise SocialError(_("The state parameter is invalid."))

        # Get the access token from the API.
        url = 'https://www.googleapis.com/oauth2/v4/token'
        data = dict(
            client_id=self.config['client_id'],
            client_secret=self.config['client_secret'],
            redirect_uri=self.config['redirect_uri'],
            code=uri_params['code'],
            grant_type='authorization_code',
        )
        r = requests.post(url, data=data)
        access_token = self.response_to_dict(r)['access_token']

        # Grab the user from the API.
        url = 'https://www.googleapis.com/plus/v1/people/me'
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer %s' % access_token,
        }
        r = requests.get(url, headers=headers, params={'prettyPrint': 'false'})
        raw = self.response_to_dict(r)
        user = User()
        user.set_raw(raw)
        user.map(
            id=raw['id'],
            name=raw['displayName'],
            email=raw['emails'][0]['value'],
            avatar=raw['image']['url'],
        )
        return user

    def response_to_dict(self, response):
        """Helper to gracefully return error messages from API."""
        output = response.json()
        if response.status_code != 200:
            raise SocialProviderError(output['message'])
        if 'error' in output:
            raise SocialProviderError(output['error'])
        return output


# Make a consistent reference for the Manager to use.
provider = GoogleProvider
