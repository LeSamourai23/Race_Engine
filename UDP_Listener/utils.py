def seconds_to_lap_time(seconds):
    prefix = ""
    if seconds < 0:
        prefix = "-"
        seconds *= -1

    minutes = seconds // 60
    remaining = seconds % 60
    return prefix + "{:01.0f}:{:06.3f}".format(minutes, remaining)