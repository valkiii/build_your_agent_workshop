# autoquit.py — stop the local Streamlit server when the browser tab goes away,
# so a background launch doesn't leave it running forever. A daemon thread
# watches the active-session count; the "Quit" button calls quit_now() directly.
import os
import signal
import threading
import time

_started = False


def quit_now():
    os.kill(os.getpid(), signal.SIGTERM)


def start(idle_seconds):
    """Begin watching. No-op if idle_seconds is 0/None or already started."""
    global _started
    if _started or not idle_seconds:
        return
    _started = True
    threading.Thread(target=_watch, args=(int(idle_seconds),), daemon=True).start()


def _watch(idle_seconds):
    seen_client = False
    empty_since = None
    while True:
        time.sleep(5)
        try:
            from streamlit.runtime import get_instance
            rt = get_instance()
            active = rt._session_mgr.num_active_sessions() if rt else 0
        except Exception:
            return  # Streamlit internals changed — rely on the Quit button instead
        if active > 0:
            seen_client, empty_since = True, None
        elif seen_client:
            empty_since = empty_since or time.monotonic()
            if time.monotonic() - empty_since >= idle_seconds:
                quit_now()
                return
