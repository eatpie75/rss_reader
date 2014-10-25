from pytz import timezone as tz


def timezone(date, timezone):
	timezone=tz(timezone)
	return date.astimezone(timezone)
