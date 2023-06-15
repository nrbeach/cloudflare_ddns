#!/usr/bin/env python3
import json
import logging
import os
import sys
from enum import IntEnum

import requests
from structlog import wrap_logger
from structlog.processors import LogfmtRenderer


def filter_secrets(_, __, event_dict):
    if "token" in event_dict:
        token = event_dict.get("token")
        if token:
            event_dict["token"] = "********"
            event_dict["event"].replace(token, "********")
    return event_dict


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

log = wrap_logger(
    logging.getLogger(__name__),
    processors=[
        filter_secrets,
        LogfmtRenderer(key_order=["event"], bool_as_flag=False),
    ],
)


class ExitCodes(IntEnum):
    SUCCESS = 0
    HTTP_ERROR = 1
    JSON_ERROR = 2
    ENVVAR_NOT_FOUND = 3
    UNKNOWN_ERROR = 255


def main(args) -> int:
    log.info("Starting", arg_len=len(args))
    rc = 0
    try:
        api_token = get_api_token()
        for arg in args:
            data = json.loads(arg)
            host_ip = get_host_ip()
            for zone_id, records in data.items():
                for record in records:
                    set_a_record(
                        api_token=api_token,
                        ip=host_ip,
                        zone_id=zone_id,
                        record_id=record["record_id"],
                        name=record["name"],
                        proxied=record["proxied"],
                    )
    except requests.HTTPError:
        rc = ExitCodes.HTTP_ERROR
    except json.JSONDecodeError as e:
        log.error(e, api_token=api_token)
        rc = ExitCodes.JSON_ERROR
    except KeyError:
        rc = ExitCodes.ENVVAR_NOT_FOUND
    except Exception as e:
        log.error(str(e))
        rc = ExitCodes.UNKNOWN_ERROR
    finally:
        log.info("Exiting.", return_code=rc)
        return rc


def get_api_token() -> str:
    api_token = os.getenv("API_TOKEN")
    if not api_token:
        log.error("API_TOKEN env var not present.")
        raise KeyError("API_TOKEN env var not present.")
    api_token = api_token.strip()
    return api_token


def get_host_ip():
    url = "http://ifconfig.co/json"
    resp = requests.get(url)
    if not resp.ok:
        log.error("Invalid Response Code", status_code=resp.status_code, url=url)
        raise requests.HTTPError(f"Invalid Response Code: {resp.status_code}")
    data = json.loads(resp.text)
    return data["ip"]


def set_a_record(api_token, zone_id, record_id, name, ip, proxied):
    url = (
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    )
    resp = requests.put(
        url,
        json={"type": "A", "name": name, "content": ip, "proxied": proxied, "ttl": 1},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}",
        },
    )
    if not resp.ok:
        log.error(
            "Invalid Response Code",
            status_code=resp.status_code,
            url=url,
            text=resp.text,
            token=api_token,
        )
        raise requests.HTTPError(f"Invalid Response: {resp.status_code}")
    data = json.loads(resp.text)
    if data["errors"]:
        # TODO different exception type
        log.error(
            "Failed to update.",
            host=name,
            host_ip=ip,
            record_id=record_id,
            zone_id=zone_id,
            proxied=proxied,
        )
        raise ValueError(
            f"Response contained {len(data['errors'])} errors. {data['errors']}"
        )
    log.info(
        "Successfully updated.",
        host=name,
        host_ip=ip,
        record_id=record_id,
        zone_id=zone_id,
        proxied=proxied,
    )


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv[1:]))
