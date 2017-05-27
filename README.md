# Popular

[![Build Status](https://api.travis-ci.org/ryannjohnson/popular-python.svg?branch-master)](https://travis-ci.org/ryannjohnson/popular-python)
[![PyPI version](https://img.shields.io/pypi/v/popular.svg)](https://pypi.python.org/pypi/popular)

This is a minimalist Python package to provide social authentication support without binding it to any particular implementation.

## Installation

Install via pip:

```bash
$ pip install popular
```

## Usage

Popular is a library and doesn't assume anything about the application environment.

_WARNING: This package is still in alpha, so the API may change._

```py
from popular import Popular

# Setup the configuration once for any available providers.
manager = Popular({
    'facebook': {
        'client_id': '12345678',
        'client_secret': 'af873927ecb2',
        'redirect_uri': 'https://example.com/callback',
    },
    'github': {
        'client_id': '12345678',
        'client_secret': 'af873927ecb2',
        'redirect_uri': 'https://example.com/callback',
    },
    'google': {
        'client_id': '12345678',
        'client_secret': 'af873927ecb2',
        'redirect_uri': 'https://example.com/callback',
    },
})

# Get the authorization link for the user.
url = manager.provider('facebook').get_auth_url(state='randomstring1')

# Use the resulting URL to get the user information from the service.
user = manager.provider('facebook').get_user(
    uri='https://example.com/callback?code=abc123&state=randomstring1',
    state='randomstring1',
)
print(user.to_dict())
```

On success, the print statement will product something like this:

```py
{
    'id': 'str_or_int',
    'name': 'Dennis Reynolds',
    'nickname': 'dreynolds',
    'email': 'email@example.com',
    'avatar': 'https://example.com/image.png'
}
```

All providers guarantee the `id` and `name` fields, and the rest may or may not appear, depending on the service and the particular user (Facebook users may not have emails if they signed up with a phone number).

### What is the `state` parameter?

Its use is outlined in [https://tools.ietf.org/html/rfc6749#section-4.1.1](https://tools.ietf.org/html/rfc6749#section-4.1.1).

Basically, a `state` string should be randomly generated when a visitor wants to authenticate via a provider and saved to the visitor's session.

When the user is redirected back to the application, the `get_user()` call must supply the same `state` string as it did for the `get_auth_url()` call.

```py
session.state = generate_random_string()
provider.get_auth_url(state=session.state)
...
provider.get_user(uri='...', state=session.state)
```
