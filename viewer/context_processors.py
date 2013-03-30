from django.conf import settings
from models import GAME_TYPES, RANKED_SOLO_QUEUE_TYPES, RANKED_GAME_TYPES


def ajax_base(request):
	return {'AJAX_BASE':settings.AJAX_BASE}


def game_types(request):
	return {'GAME_TYPES':{
		'GAME_TYPES':				GAME_TYPES,
		'RANKED_SOLO_QUEUE_TYPES':	RANKED_SOLO_QUEUE_TYPES,
		'RANKED_GAME_TYPES':		RANKED_GAME_TYPES
	}}
