"""
Contains all the URLs for the UserInfo Support App
"""

from django.conf.urls import patterns, url

from openedx.core.djangoapps.userinfo import views

urlpatterns = patterns(
    '',
    url(r'^save_identification$', 'openedx.core.djangoapps.userinfo.views.save_national_id', name='userinfo_save_national_id'),
)
