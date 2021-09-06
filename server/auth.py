from typing import List
from os import environ

"""
controller generated to handled auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""
def check_apikey(api_key, required_scopes):
    if api_key == environ["API_KEY"]:
        return {'api_key': api_key }
    return None

