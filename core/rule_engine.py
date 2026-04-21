"""Rule engine implementation for Chronobar platform."""

import logging
from datetime import datetime, time, date
from typing import Any

from core.enums import SessionType
from core.exceptions import ChronobarError


logger = logging.getLogger(__name__)


class RuleEngineError(ChronobarError):
    """Exception raised for rule engine errors."""
    pass


class SessionSegment:
    """Represents a time segment within a session."""

    def __init__(self, session_type: SessionType, start: str, end: str):
        """Initialize session segment.

        Args:
            session_type: Type of session (morning, afternoon, night)
            start: Start time in HH:MM format
            end: End time in HH:MM format
        """
        self.session_type = session_type
        self.start = datetime.strptime(start, "%H:%M").time()
        self.end = datetime.strptime(end, "%H:%M").time()


class SessionTemplate:
    """Template for trading sessions."""

    def __init__(
        self,
        template_id: str,
        exchange: str,
        trading_date_rule: str,
        segments: list[dict[str, Any]],
    ):
        """Initialize session template.

        Args:
            template_id: Template identifier
            exchange: Exchange code
            trading_date_rule: Rule for determining trading date
            segments: List of session segments
        """
        self.template_id = template_id
        self.exchange = exchange
        self.trading_date_rule = trading_date_rule
        self.segments: list[SessionSegment] = []

        for seg in segments:
            session_type = SessionType(seg["type"])
            segment = SessionSegment(session_type, seg["start"], seg["end"])
            self.segments.append(segment)


class RuleEngine:
    """Rule engine for session determination and trading date calculation."""

    def __init__(self, session_templates: dict[str, SessionTemplate] | None = None):
        """Initialize rule engine.

        Args:
            session_templates: Dictionary of session templates keyed by template_id
        """
        self._session_templates: dict[str, SessionTemplate] = session_templates or {}

    def load_session_template(self, template_id: str, config: dict[str, Any]) -> None:
        """Load a session template from config.

        Args:
            template_id: Template identifier
            config: Configuration dictionary
        """
        template_config = config.get("session_templates", {}).get(template_id)
        if not template_config:
            raise RuleEngineError(f"Session template {template_id} not found in config")

        template = SessionTemplate(
            template_id=template_id,
            exchange=template_config["exchange"],
            trading_date_rule=template_config["trading_date_rule"],
            segments=template_config["segments"],
        )
        self._session_templates[template_id] = template
        logger.info(f"Loaded session template: {template_id}")

    def determine_session(
        self, dt: datetime, template_id: str
    ) -> tuple[SessionType, time, time]:
        """Determine session type and segment for a given datetime.

        Args:
            dt: Datetime to check
            template_id: Session template to use

        Returns:
            Tuple of (session_type, segment_start, segment_end)

        Raises:
            RuleEngineError: If template not found or no matching segment
        """
        template = self._session_templates.get(template_id)
        if not template:
            raise RuleEngineError(f"Session template {template_id} not loaded")

        current_time = dt.time()

        for segment in template.segments:
            if segment.start <= current_time < segment.end:
                return segment.session_type, segment.start, segment.end

        # Check if it's in a night session that crosses day boundary
        for segment in template.segments:
            if segment.session_type == SessionType.NIGHT and segment.start > segment.end:
                # Night session crosses midnight
                if current_time >= segment.start or current_time < segment.end:
                    return segment.session_type, segment.start, segment.end

        raise RuleEngineError(f"Time {current_time} does not fall within any session segment")

    def calculate_trading_date(
        self, dt: datetime, template_id: str, calendar_date: date
    ) -> date:
        """Calculate trading date based on datetime and template rule.

        Args:
            dt: Datetime to check
            template_id: Session template to use
            calendar_date: Calendar date (natural date)

        Returns:
            Trading date

        Raises:
            RuleEngineError: If template not found or rule not supported
        """
        template = self._session_templates.get(template_id)
        if not template:
            raise RuleEngineError(f"Session template {template_id} not loaded")

        session_type, _, _ = self.determine_session(dt, template_id)

        if template.trading_date_rule == "night_belongs_next_trading_date":
            # Night session belongs to the next trading date
            if session_type == SessionType.NIGHT:
                # Check if night session crosses midnight
                night_segment = next(
                    (s for s in template.segments if s.session_type == SessionType.NIGHT),
                    None,
                )
                if night_segment and night_segment.start > night_segment.end:
                    # Night session crosses midnight, trading date is the next day
                    return calendar_date
                else:
                    # Night session doesn't cross midnight, trading date is next day
                    return date.fromordinal(calendar_date.toordinal() + 1)
            # Morning and afternoon sessions belong to the same trading date
            return calendar_date
        else:
            raise RuleEngineError(
                f"Trading date rule {template.trading_date_rule} not supported"
            )

    def is_cross_day_session(self, template_id: str, session_type: SessionType) -> bool:
        """Check if a session type crosses day boundary.

        Args:
            template_id: Session template to use
            session_type: Session type to check

        Returns:
            True if session crosses day boundary
        """
        template = self._session_templates.get(template_id)
        if not template:
            raise RuleEngineError(f"Session template {template_id} not loaded")

        segment = next(
            (s for s in template.segments if s.session_type == session_type), None
        )
        if not segment:
            return False

        return segment.start > segment.end
