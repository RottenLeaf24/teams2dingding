import json,yaml
import logging

import requests
import os, atexit, msal

# Optional logging
# logging.basicConfig(level=logging.DEBUG)  # Enable DEBUG log for entire script
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logging.getLogger("msal").setLevel(logging.INFO)  # Optionally disable MSAL DEBUG logs

# config = json.load(open('config.json'))
config = yaml.full_load(open('config.yaml'))['microsoftgraph']


def gene_token():
    cache = msal.SerializableTokenCache()
    if os.path.exists("my_cache.bin"):
        cache.deserialize(open("my_cache.bin", "r").read())
    atexit.register(lambda:
                    open("my_cache.bin", "w").write(cache.serialize())
                    # Hint: The following optional line persists only when state changed
                    if cache.has_state_changed else None
                    )
    # Create a preferably long-lived app instance which maintains a token cache.
    app = msal.PublicClientApplication(
        config["client_id"], authority=config["authority"], token_cache=cache
        # token_cache=...  # Default cache is in memory only.
        # You can learn how to use SerializableTokenCache from
        # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
    )

    # The pattern to acquire a token looks like this.
    result = None

    # Firstly, check the cache to see if this end user has signed in before
    accounts = app.get_accounts(username=config["username"])
    if accounts:
        logging.info("Account(s) exists in cache, probably with token too. Let's try.")
        result = app.acquire_token_silent(config["scope"], account=accounts[0])

    if not result:
        logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
        # See this page for constraints of Username Password Flow.
        # https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki/Username-Password-Authentication
        result = app.acquire_token_by_username_password(
            config["username"], config["password"], scopes=config["scope"])
    return result['access_token']
