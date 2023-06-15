from unittest.mock import patch

import pytest
import requests

from cloudflare_ddns import get_api_token
from cloudflare_ddns import get_host_ip
from cloudflare_ddns import set_a_record


@pytest.fixture
def api_key():
    return "123456789"


@pytest.fixture
def ifconfigco_json():
    return """
    {
  "ip": "10.11.12.13",
  "ip_decimal": 1438212595,
  "country": "United States",
  "country_iso": "US",
  "country_eu": false,
  "region_name": "Unknown",
  "region_code": "UK",
  "metro_code": 500,
  "zip_code": "99999",
  "city": "Unknown",
  "latitude": 0.0111,
  "longitude": -0.675,
  "time_zone": "America/Los_Angeles"
}"""


@patch("requests.get")
def test_get_host_ip_happy_path(mock_get, ifconfigco_json):
    mock_get.return_value.ok = True
    mock_get.return_value.text = ifconfigco_json
    assert get_host_ip() == "10.11.12.13"


@patch("requests.get")
def test_get_host_ip_incorrect_status_code_raises(mock_get, ifconfigco_json):
    mock_get.return_value.ok = False
    with pytest.raises(requests.HTTPError):
        get_host_ip()


def test_get_api_key(api_key, monkeypatch):
    monkeypatch.setenv("API_TOKEN", "123456789")
    assert get_api_token() == api_key


@patch("requests.put")
def test_set_a_record_happy_path(mock_put):
    mock_put.return_value.ok = True
    mock_put.return_value.text = """{"errors": []}"""
    set_a_record("123456789", "123", "456", "foo.com", "10.10.10.10", True)


@patch("requests.put")
def test_set_a_record_invalid_response(mock_put):
    mock_put.return_value.ok = False
    mock_put.return_value.text = """{"errors": []}"""
    with pytest.raises(requests.HTTPError):
        set_a_record("123456789", "123", "456", "foo.com", "10.10.10.10", True)


@patch("requests.put")
def test_set_a_record_response_body_has_errors(mock_put):
    mock_put.return_value.ok = True
    mock_put.return_value.text = """{"errors": ["invalid record type"]}"""
    with pytest.raises(ValueError):
        set_a_record("123456789", "123", "456", "foo.com", "10.10.10.10", True)
