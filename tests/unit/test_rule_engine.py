"""Unit tests for rule engine."""

from datetime import datetime, time, date

import pytest

from core.enums import SessionType
from core.rule_engine import RuleEngine, RuleEngineError, SessionTemplate, SessionSegment


def test_session_segment_creation():
    """Test SessionSegment can be created."""
    segment = SessionSegment(SessionType.MORNING, "09:00", "10:15")
    assert segment.session_type == SessionType.MORNING
    assert segment.start == time(9, 0)
    assert segment.end == time(10, 15)


def test_session_template_creation():
    """Test SessionTemplate can be created."""
    segments = [
        {"type": "morning", "start": "09:00", "end": "10:15"},
        {"type": "morning", "start": "10:30", "end": "11:30"},
        {"type": "afternoon", "start": "13:30", "end": "15:00"},
        {"type": "night", "start": "21:00", "end": "23:00"},
    ]
    template = SessionTemplate(
        template_id="SHFE_A_NIGHT_2300",
        exchange="SHFE",
        trading_date_rule="night_belongs_next_trading_date",
        segments=segments,
    )
    assert template.template_id == "SHFE_A_NIGHT_2300"
    assert template.exchange == "SHFE"
    assert len(template.segments) == 4


def test_rule_engine_determine_session_morning():
    """Test session determination for morning session."""
    config = {
        "session_templates": {
            "SHFE_A_NIGHT_2300": {
                "exchange": "SHFE",
                "trading_date_rule": "night_belongs_next_trading_date",
                "segments": [
                    {"type": "morning", "start": "09:00", "end": "10:15"},
                    {"type": "morning", "start": "10:30", "end": "11:30"},
                    {"type": "afternoon", "start": "13:30", "end": "15:00"},
                    {"type": "night", "start": "21:00", "end": "23:00"},
                ],
            }
        }
    }
    engine = RuleEngine()
    engine.load_session_template("SHFE_A_NIGHT_2300", config)

    # Test morning session 09:30
    dt = datetime(2025, 1, 15, 9, 30)
    session_type, start, end = engine.determine_session(dt, "SHFE_A_NIGHT_2300")
    assert session_type == SessionType.MORNING
    assert start == time(9, 0)
    assert end == time(10, 15)


def test_rule_engine_determine_session_afternoon():
    """Test session determination for afternoon session."""
    config = {
        "session_templates": {
            "SHFE_A_NIGHT_2300": {
                "exchange": "SHFE",
                "trading_date_rule": "night_belongs_next_trading_date",
                "segments": [
                    {"type": "morning", "start": "09:00", "end": "10:15"},
                    {"type": "morning", "start": "10:30", "end": "11:30"},
                    {"type": "afternoon", "start": "13:30", "end": "15:00"},
                    {"type": "night", "start": "21:00", "end": "23:00"},
                ],
            }
        }
    }
    engine = RuleEngine()
    engine.load_session_template("SHFE_A_NIGHT_2300", config)

    # Test afternoon session 14:00
    dt = datetime(2025, 1, 15, 14, 0)
    session_type, start, end = engine.determine_session(dt, "SHFE_A_NIGHT_2300")
    assert session_type == SessionType.AFTERNOON
    assert start == time(13, 30)
    assert end == time(15, 0)


def test_rule_engine_determine_session_night():
    """Test session determination for night session."""
    config = {
        "session_templates": {
            "SHFE_A_NIGHT_2300": {
                "exchange": "SHFE",
                "trading_date_rule": "night_belongs_next_trading_date",
                "segments": [
                    {"type": "morning", "start": "09:00", "end": "10:15"},
                    {"type": "morning", "start": "10:30", "end": "11:30"},
                    {"type": "afternoon", "start": "13:30", "end": "15:00"},
                    {"type": "night", "start": "21:00", "end": "23:00"},
                ],
            }
        }
    }
    engine = RuleEngine()
    engine.load_session_template("SHFE_A_NIGHT_2300", config)

    # Test night session 22:00
    dt = datetime(2025, 1, 15, 22, 0)
    session_type, start, end = engine.determine_session(dt, "SHFE_A_NIGHT_2300")
    assert session_type == SessionType.NIGHT
    assert start == time(21, 0)
    assert end == time(23, 0)


def test_rule_engine_determine_session_outside_hours():
    """Test session determination for time outside trading hours."""
    config = {
        "session_templates": {
            "SHFE_A_NIGHT_2300": {
                "exchange": "SHFE",
                "trading_date_rule": "night_belongs_next_trading_date",
                "segments": [
                    {"type": "morning", "start": "09:00", "end": "10:15"},
                    {"type": "morning", "start": "10:30", "end": "11:30"},
                    {"type": "afternoon", "start": "13:30", "end": "15:00"},
                    {"type": "night", "start": "21:00", "end": "23:00"},
                ],
            }
        }
    }
    engine = RuleEngine()
    engine.load_session_template("SHFE_A_NIGHT_2300", config)

    # Test time outside trading hours 16:00
    dt = datetime(2025, 1, 15, 16, 0)
    with pytest.raises(RuleEngineError):
        engine.determine_session(dt, "SHFE_A_NIGHT_2300")


def test_rule_engine_calculate_trading_date_morning():
    """Test trading date calculation for morning session."""
    config = {
        "session_templates": {
            "SHFE_A_NIGHT_2300": {
                "exchange": "SHFE",
                "trading_date_rule": "night_belongs_next_trading_date",
                "segments": [
                    {"type": "morning", "start": "09:00", "end": "10:15"},
                    {"type": "morning", "start": "10:30", "end": "11:30"},
                    {"type": "afternoon", "start": "13:30", "end": "15:00"},
                    {"type": "night", "start": "21:00", "end": "23:00"},
                ],
            }
        }
    }
    engine = RuleEngine()
    engine.load_session_template("SHFE_A_NIGHT_2300", config)

    # Morning session belongs to same trading date
    dt = datetime(2025, 1, 15, 9, 30)
    calendar_date = date(2025, 1, 15)
    trading_date = engine.calculate_trading_date(dt, "SHFE_A_NIGHT_2300", calendar_date)
    assert trading_date == date(2025, 1, 15)


def test_rule_engine_calculate_trading_date_night():
    """Test trading date calculation for night session."""
    config = {
        "session_templates": {
            "SHFE_A_NIGHT_2300": {
                "exchange": "SHFE",
                "trading_date_rule": "night_belongs_next_trading_date",
                "segments": [
                    {"type": "morning", "start": "09:00", "end": "10:15"},
                    {"type": "morning", "start": "10:30", "end": "11:30"},
                    {"type": "afternoon", "start": "13:30", "end": "15:00"},
                    {"type": "night", "start": "21:00", "end": "23:00"},
                ],
            }
        }
    }
    engine = RuleEngine()
    engine.load_session_template("SHFE_A_NIGHT_2300", config)

    # Night session belongs to next trading date
    dt = datetime(2025, 1, 15, 22, 0)
    calendar_date = date(2025, 1, 15)
    trading_date = engine.calculate_trading_date(dt, "SHFE_A_NIGHT_2300", calendar_date)
    assert trading_date == date(2025, 1, 16)


def test_rule_engine_is_cross_day_session():
    """Test cross-day session detection."""
    config = {
        "session_templates": {
            "SHFE_A_NIGHT_2300": {
                "exchange": "SHFE",
                "trading_date_rule": "night_belongs_next_trading_date",
                "segments": [
                    {"type": "morning", "start": "09:00", "end": "10:15"},
                    {"type": "night", "start": "21:00", "end": "02:00"},
                ],
            }
        }
    }
    engine = RuleEngine()
    engine.load_session_template("SHFE_A_NIGHT_2300", config)

    # Morning session does not cross day
    assert not engine.is_cross_day_session("SHFE_A_NIGHT_2300", SessionType.MORNING)

    # Night session crosses day
    assert engine.is_cross_day_session("SHFE_A_NIGHT_2300", SessionType.NIGHT)
