import json
from unittest.mock import patch

import pytest
import requests
import responses
from pydantic import ValidationError

from clientes import ClinicalTrial, ClinicalTrialsExtractor


@responses.activate
def test_get_trials_200_response():
    mock_url = (
        "https://clinicaltrials.gov/api/v2/studies?query.cond=epilepsy&pageSize=100"
    )
    mock_json_payload = {
        "studies": [
            {
                "protocolSection": {
                    "identificationModule": {
                        "nctId": "NCT01234567",
                        "briefTitle": "Mocked Trial",
                    },
                    "statusModule": {"overallStatus": "COMPLETED"},
                    "designModule": {"enrollmentInfo": {"count": 150}},
                }
            }
        ]
    }

    responses.add(
        method=responses.GET, url=mock_url, json=mock_json_payload, status=200
    )
    extractor = ClinicalTrialsExtractor(cache_name="ct_api_cache")
    result = extractor.get_trials(condition="epilepsy", max_records=300)
    study = result[0]["protocolSection"]

    assert isinstance(result, list)
    assert len(result) == 1
    assert study["identificationModule"]["nctId"] == "NCT01234567"
    assert study["statusModule"]["overallStatus"] == "COMPLETED"


@responses.activate
def test_429_then_retry_then_200():
    mock_url = (
        "https://clinicaltrials.gov/api/v2/studies?query.cond=epilepsy&pageSize=100"
    )
    call_tracker = []

    def request_callback(request):
        call_tracker.append(1)
        if len(call_tracker) == 1:
            return (429, {}, '{"error": "Too Many Requests"}')  # respuesta 429
        else:
            mock_json_payload = {
                "studies": [
                    {
                        "protocolSection": {
                            "identificationModule": {
                                "nctId": "NCT01234567",
                                "briefTitle": "Mocked Trial",
                            },
                            "statusModule": {"overallStatus": "COMPLETED"},
                            "designModule": {"enrollmentInfo": {"count": 150}},
                        }
                    }
                ]
            }
            return (200, {}, json.dumps(mock_json_payload))  # seguido de respuesta 200

    responses.add_callback(
        method=responses.GET,
        url=mock_url,
        callback=request_callback,
        content_type="application/json",
    )

    extractor = ClinicalTrialsExtractor(cache_name="test_api_cache")
    extractor.session.cache.clear()
    result = extractor.get_trials(condition="epilepsy", max_records=300)

    assert isinstance(result, list)
    assert len(result) == 1
    assert (
        result[0]["protocolSection"]["identificationModule"]["nctId"] == "NCT01234567"
    )
    assert len(call_tracker) == 2


@responses.activate
@patch("urllib3.util.retry.time.sleep")
def test_n_times_500_then_gives_up(mock_sleep):
    mock_url = (
        "https://clinicaltrials.gov/api/v2/studies?query.cond=epilepsy&pageSize=100"
    )
    responses.add(
        method=responses.GET,
        url=mock_url,
        json={"error": "Internal Server Error"},
        status=500,
    )
    extractor = ClinicalTrialsExtractor(cache_name="test_api_cache_fails")
    with pytest.raises(requests.exceptions.RetryError):
        extractor.get_trials(condition="epilepsy", max_records=300)

    assert len(responses.calls) == 6  # reintenta 5 veces y luego se rinde


@responses.activate
def test_404_does_not_trigger_retry():
    mock_url = (
        "https://clinicaltrials.gov/api/v2/studies?query.cond=epilepsy&pageSize=100"
    )
    responses.add(
        method=responses.GET, url=mock_url, json={"error": "Not Found"}, status=404
    )
    extractor = ClinicalTrialsExtractor(cache_name="test_api_cache_404")
    extractor.session.cache.clear()
    with pytest.raises(requests.exceptions.HTTPError):
        extractor.get_trials(condition="epilepsy", max_records=300)
    assert len(responses.calls) == 1  # solo intenta una vez y falla


def test_pydantic_rejects_missing_title():
    bad_raw_study = {
        "protocolSection": {
            "identificationModule": {
                "nctId": "NCT01234567"  # sin titulo
            },
            "statusModule": {"overallStatus": "COMPLETED"},
            "designModule": {"enrollmentInfo": {"count": 150}},
        }
    }

    with pytest.raises(ValidationError) as exc_info:
        ClinicalTrial(**bad_raw_study)

    error_msg = str(exc_info.value)
    assert "title" in error_msg
    assert "Input should be a valid string" in error_msg
