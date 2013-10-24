from django.conf import settings


def ajax_base(request):
	return {'AJAX_BASE':settings.AJAX_BASE}
