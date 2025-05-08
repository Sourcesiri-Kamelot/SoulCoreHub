import logging
import os
import platform
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv
from posthog import Posthog

from airtrain.telemetry.views import BaseTelemetryEvent

load_dotenv()

logger = logging.getLogger(__name__)

# Enhanced event settings to collect more data
POSTHOG_EVENT_SETTINGS = {
    'process_person_profile': True,
    'enable_sent_at': True,  # Add timing information
    'capture_performance': True,  # Collect performance data
    'capture_pageview': True,  # More detailed usage tracking
}


def singleton(cls):
    """Singleton decorator for classes."""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class ProductTelemetry:
    """
    Service for capturing telemetry data from Airtrain usage.

    Telemetry is enabled by default but can be disabled by setting 
    AIRTRAIN_TELEMETRY_ENABLED=false in your environment.
    """

    USER_ID_PATH = str(
        Path.home() / '.cache' / 'airtrain' / 'telemetry_user_id'
    )
    # API key for PostHog
    PROJECT_API_KEY = 'phc_1pLNkG3QStYEXIz0CAPQaOGpcmxpE3CJXhE1HANWgIz'
    HOST = 'https://us.i.posthog.com'
    UNKNOWN_USER_ID = 'UNKNOWN'

    _curr_user_id = None

    def __init__(self) -> None:
        telemetry_disabled = os.getenv('AIRTRAIN_TELEMETRY_ENABLED', 'true').lower() == 'false'
        self.debug_logging = os.getenv('AIRTRAIN_LOGGING_LEVEL', 'info').lower() == 'debug'
        
        # System information to include with telemetry
        self.system_info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'platform': platform.platform(),
            'machine': platform.machine(),
            'hostname': platform.node(),
            'username': os.getlogin() if hasattr(os, 'getlogin') else 'unknown'
        }
        isBeta = True  # TODO: remove this once out of beta
        if telemetry_disabled and not isBeta:
            self._posthog_client = None
        else:
            if not isBeta:
                logging.info(
                    'Telemetry enabled. To disable, set '
                    'AIRTRAIN_TELEMETRY_ENABLED=false in your environment.'
                )
            if isBeta:
                logging.info(
                    'You are currently in beta. Telemetry is enabled by default.'
                )
            self._posthog_client = Posthog(
                project_api_key=self.PROJECT_API_KEY,
                host=self.HOST,
                disable_geoip=False  # Collect geographical data
            )

            # Set debug mode if enabled
            if self.debug_logging:
                self._posthog_client.debug = True

            # Identify user more specifically
            self._posthog_client.identify(
                self.user_id,
                {
                    **self.system_info,
                    'first_seen': True
                }
            )

            # Silence posthog's logging only if debug is off
            if not self.debug_logging:
                posthog_logger = logging.getLogger('posthog')
                posthog_logger.disabled = True

        if self._posthog_client is None:
            logger.debug('Telemetry disabled')

    def capture(self, event: BaseTelemetryEvent) -> None:
        """Capture a telemetry event and send it to PostHog if telemetry is enabled."""
        if self._posthog_client is None:
            return

        # Add system information to all events
        enhanced_properties = {
            **event.properties,
            **POSTHOG_EVENT_SETTINGS,
            **self.system_info
        }

        if self.debug_logging:
            logger.debug(f'Telemetry event: {event.name} {enhanced_properties}')
        self._direct_capture(event, enhanced_properties)

    def _direct_capture(self, event: BaseTelemetryEvent, enhanced_properties: dict) -> None:
        """
        Send the event to PostHog. Should not be thread blocking because posthog handles it.
        """
        if self._posthog_client is None:
            return

        try:
            self._posthog_client.capture(
                self.user_id,
                event.name,
                enhanced_properties
            )
        except Exception as e:
            logger.error(f'Failed to send telemetry event {event.name}: {e}')

    @property
    def user_id(self) -> str:
        """
        Get the user ID for telemetry.
        Creates a new one if it doesn't exist.
        """
        if self._curr_user_id:
            return self._curr_user_id

        # File access may fail due to permissions or other reasons.
        # We don't want to crash so we catch all exceptions.
        try:
            if not os.path.exists(self.USER_ID_PATH):
                os.makedirs(os.path.dirname(self.USER_ID_PATH), exist_ok=True)
                with open(self.USER_ID_PATH, 'w') as f:
                    # Use a more identifiable ID prefix
                    new_user_id = f"airtrain-user-{uuid.uuid4()}"
                    f.write(new_user_id)
                self._curr_user_id = new_user_id
            else:
                with open(self.USER_ID_PATH, 'r') as f:
                    self._curr_user_id = f.read()
        except Exception:
            self._curr_user_id = self.UNKNOWN_USER_ID
        return self._curr_user_id 