#!/usr/bin/env python3
import requests

from core.config import settings
from logger import logger


def check_google_safebrowsing(url: str, local=False) -> bool:
    baseurl = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    params = f"key={settings.google_api_key}"
    headers = {"Content-Type": "application/json"}
    body = {
        "client": {"clientId": "no_phish_nft", "clientVersion": "0.0.1"},
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "THREAT_TYPE_UNSPECIFIED",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION",
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL", "THREAT_ENTRY_TYPE_UNSPECIFIED", "EXECUTABLE"],
            "threatEntries": [{"url": url}],
        },
    }
    return requests.post(f"{baseurl}?{params}", headers=headers, json=body).json()
