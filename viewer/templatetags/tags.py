from coffin import template
# from datetime import datetime
from pytz import timezone as tz

register = template.Library()


# @register.filter
def timezone(date, timezone):
	timezone=tz(timezone)
	print('wat')
	print(date.astimezone(timezone))
	return date.astimezone(timezone)
