import logging
from django.contrib.auth.models import User
from django.http import (
            HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpRequest
)
from national_id.models import ExtraInfo

def set_national_id(request):
    if request.method == "POST":
        if request.user.is_authenticated():
            username = request.user.username
            try:
                user = User.objects.get(username=username)
                identification = request.POST.get("identification")
                national_id = ExtraInfo.objects.get(national_id=identification)
                if identification == '':
                    msg="Passport or National ID number can not be empty"
                    return HttpResponse(msg,status=403)
                msg="National Number already in use"
                logger.error('Error thrown when updating Passport or National ID number of user {username}. ERROR: {exception}'.format(username=username, exception="National Number already in use"))
                return HttpResponse(msg,status=403)
            except User.DoesNotExist:
                msg="User invalid"
                logger.error('Error thrown when updating Passport or National ID number of user {username}. ERROR: {exception}'.format(username=username, exception=exception))
                return HttpResponse(msg,status=403)
            except ExtraInfo.DoesNotExist:
                national_id = ExtraInfo()
                national_id.set_dni(user,identification)
                msg="Ok"
                return HttpResponse(msg,status=200)
