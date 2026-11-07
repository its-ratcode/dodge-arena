"""Time formatting for display."""


def fmt_time(seconds: float) -> str:
    """Survival time as ``m:ss.t``, e.g. 65.34 -> "1:05.3"."""
    tenths = int(seconds * 10)                  # truncate: never show time not yet survived
    minutes, rest = divmod(tenths, 600)
    return f"{minutes}:{rest // 10:02d}.{rest % 10}"
