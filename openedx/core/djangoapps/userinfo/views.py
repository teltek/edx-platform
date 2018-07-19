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
        return HttpResponseBadRequest(_("National Id not given. You need to specify your National Identity Number."))
        
    if not user_national_id:
        try:
            national_object = NationalId.objects.create(user=user,national_id=national_id)
            national_object.save()
            data = {'message': 'Created new National Id'}
            return HttpResponse(json.dumps(data), content_type="application/json")
        except Exception as exception:
            log.error('exception: {}'.format(exception))
            message = (_("Error on saving National Id '{national_id}' of user '{username}': {exception}")).format(national_id=national_id,username=user.username,exception=exception.message)
            log.error(message)
            return HttpResponseBadRequest(message)
    try:
        if national_id == user_national_id.national_id:
            data = {'message': 'National Id already saved'}
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            raise Exception((_("Already saved with value '{national_id}'.")).format(national_id=user_national_id.national_id))
    except Exception as exception:
        message = (_("Error on saving National Id '{national_id}' of user '{username}': {exception}")).format(national_id=national_id,username=user.username,exception=exception.message)
        log.error(message)
        return HttpResponseBadRequest(message)
        
    
def _get_national_id(user):
    try:
        return NationalId.objects.get(user=user)
    except NationalId.DoesNotExist:
        return False
    except Exception as exception:
        log.error('exception: {}'.format(exception))
        return False
    
