# SPDX-License-Identifier: GPL-2.0+

import importlib
import os
import pytest
import requests
import greenwave.monitor

MONITORING_METRICS = {
    "process_resident_memory_bytes gauge",
    "process_start_time_seconds gauge",
    "process_cpu_seconds_total counter",
    "process_open_fds gauge",
    "process_max_fds gauge",
    "process_virtual_memory_bytes gauge",
    "messaging_rx_total counter",
    "messaging_rx_ignored_total counter",
    "messaging_rx_processed_ok_total counter",
    "messaging_rx_failed_total counter",
    "messaging_tx_to_send_total counter",
    "messaging_tx_stopped_total counter",
    "messaging_tx_sent_ok_total counter",
    "messaging_tx_failed_total counter",
    "total_decision_exceptions_total counter",
    "total_decision_exceptions_created gauge",
    "decision_request_duration_seconds histogram",
    "decision_request_duration_seconds_created gauge",
    "publish_decision_exceptions_new_waiver_total counter",
    "publish_decision_exceptions_new_waiver_created gauge",
    "publish_decision_exceptions_new_result_total counter",
    "publish_decision_exceptions_new_result_created gauge",
}


def test_metrics(requests_session, greenwave_server):
    r = requests_session.get(greenwave_server + 'api/v1.0/metrics')

    assert r.status_code == 200

    actual_metrics = {
        line[7:]
        for line in r.text.splitlines()
        if line.startswith('# TYPE')
    }
    assert actual_metrics == MONITORING_METRICS


def test_standalone_metrics_server_disabled_by_default(requests_session):
    with pytest.raises(requests.exceptions.ConnectionError):
        requests_session.get('http://127.0.0.1:10040/metrics')


def test_standalone_metrics_server(requests_session):
    os.environ['MONITOR_STANDALONE_METRICS_SERVER_ENABLE'] = 'true'
    importlib.reload(greenwave.monitor)

    r = requests_session.get('http://127.0.0.1:10040/metrics')

    actual_metrics = {
        line[7:]
        for line in r.text.splitlines()
        if line.startswith('# TYPE')
    }
    assert actual_metrics == MONITORING_METRICS
