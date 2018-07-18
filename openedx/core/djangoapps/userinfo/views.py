import json

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from .models import NationalId
from django.utils.translation import ugettext as _

import logging

log = logging.getLogger(__name__)

@require_POST
@login_required
def save_national_id(request):
    """
    Check if the user has already saved the national id.
    Saves the id if not done before.
    """
    user = User.objects.get(username=request.user)
    already_saved = False
    user_national_id = _get_national_id(user)
    national_id = request.POST['national_id']
    if not national_id:
        return HttpResponseBadRequest(_("National Id not given."))
        
    if not user_national_id:
        try:
            national_object = NationalId.objects.create(user=user,national_id=national_id)
            national_object.save()
            data = {'message': 'created new National Id'}
            return HttpResponse(json.dumps(data), content_type="application/json")
        except Exception as exception:
            log.error('exception: {}'.format(exception))
            return HttpResponseBadRequest((_("Error on saving National Id '{national_id}' of user '{username}': {exception}")).format(national_id=national_id,username=user.username,exception=exception.message))    
    try:
        if national_id == user_national_id.national_id:
            log.error('national id already saved')
            data = {'message': 'National Id already saved'}
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            log.error('already saved but not the same')
            raise _("National Id already saved with another value for this same user.")
    except Exception as exception:
        log.error('exception: {}'.format(exception.message))
        return HttpResponseBadRequest((_("Error: {}.")).format(exception.message))
        
    
def _get_national_id(user):
    try:
        return NationalId.objects.get(user=user)
    except NationalId.DoesNotExist:
        return False
    except Exception as exception:
        log.error('exception: {}'.format(exception))
        return False
    
