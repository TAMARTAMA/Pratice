import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Components.publisher import Publisher  # תוודאי שזה שם הקובץ שבו שמורה המחלקה שלך

def test_single_subscriber_receives_event():
    pub = Publisher()
    results = []

    def handler(data):
        results.append(data)

    pub.subscribe("test_event", handler)
    pub.publish("test_event", "hello")

    assert results == ["hello"]


def test_multiple_subscribers_receive_event():
    pub = Publisher()
    results = []

    pub.subscribe("event", lambda data: results.append(f"A:{data}"))
    pub.subscribe("event", lambda data: results.append(f"B:{data}"))

    pub.publish("event", 123)

    assert results == ["A:123", "B:123"]


def test_multiple_subscribers_receive_event():
    pub = Publisher()
    results = []

    pub.subscribe("event", lambda data: results.append(f"A:{data}"))
    pub.subscribe("event", lambda data: results.append(f"B:{data}"))

    pub.publish("event", 123)

    assert results == ["A:123", "B:123"]


def test_no_subscriber_does_not_crash():
    pub = Publisher()
    try:
        pub.publish("unsubscribed_event", "no crash")
    except Exception as e:
        pytest.fail(f"Exception raised on no-subscriber publish: {e}")


def test_different_topics_are_isolated():
    pub = Publisher()
    results = []

    pub.subscribe("event_a", lambda data: results.append(f"A:{data}"))
    pub.subscribe("event_b", lambda data: results.append(f"B:{data}"))

    pub.publish("event_b", 7)

    assert results == ["B:7"]
