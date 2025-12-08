# File: censys_rest.py
#
# Copyright (c) 2016-2025 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
import phantom.app as phantom
import requests

from censys_consts import CENSYS_TOKEN, CENSYS_API_URL, CENSYS_ERR_JSON_DECODE
from censys_validation import get_error_message_from_exception

def make_rest_call(endpoint, action_result, config, data=None, method="post"):
    token = config[CENSYS_TOKEN]

    request_func = getattr(requests, method)

    url = f"{CENSYS_API_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}","Content-type": "application/json"}

    try:
        response = request_func(
            url,
            json=data,
            headers=headers,
        )
    except Exception as e:
        return (
            action_result.set_status(
                phantom.APP_ERROR,
                f"Unable to connect to the server. {get_error_message_from_exception(e)}",
            ),
            {},
        )

    if response.status_code not in (200, 201):
        ret_val, _ = parse_http_error(action_result, response)
        return ret_val, {}
    try:
        resp_json = response.json()
    except Exception as e:
        return (
            action_result.set_status(phantom.APP_ERROR, CENSYS_ERR_JSON_DECODE.format(e, response.text)),
            {},
        )

    return phantom.APP_SUCCESS, resp_json


def parse_http_error(action_result, response):
    try:
        resp_json = response.json()
        msg = resp_json.get("error") or resp_json.get("detail") or resp_json.get("message") or response.text
    except Exception as e:
        msg = CENSYS_ERR_JSON_DECODE.format(e, response.text)

    return action_result.set_status(phantom.APP_ERROR, msg), {}