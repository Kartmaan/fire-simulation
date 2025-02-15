timers = {}
def timer(timer_name: str, duration: float) -> bool:
    """Checks if a timer has expired.

    Args:
        timer_name (str): Timer name.
        duration (float): Desired duration in seconds.

    Returns:
        bool: True if time is up, False otherwise.
    """
    now = pygame.time.get_ticks() // 1000

    if timer_name not in timers:
        timers[timer_name] = now
        return False

    elapsed_time = now - timers[timer_name]
    if elapsed_time >= duration:
        timers[timer_name] = now
        return True

    return False