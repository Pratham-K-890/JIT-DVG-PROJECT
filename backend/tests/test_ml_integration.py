import pytest

from app.ml.inference import predict_priority, predict_spam


def test_predict_spam_returns_bool():
    assert isinstance(predict_spam("test", "test body"), bool)


def test_predict_spam_handles_none_values():
    assert isinstance(predict_spam(None, None), bool)


def test_predict_priority_returns_float_in_range():
    score = predict_priority(
        {
            "sender_frequency": 5,
            "reply_rate": 0.5,
            "has_urgent_keyword": 0,
            "hour_of_day": 12,
        }
    )
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_predict_priority_missing_key_raises_value_error():
    with pytest.raises(ValueError):
        predict_priority({"sender_frequency": 5, "reply_rate": 0.5, "hour_of_day": 12})
