from .models import NationalId
from django.forms import ModelForm

class NationalIdForm(ModelForm):
    """
    The fields on this form are derived from the NationalId model in models.py.
    """
    def __init__(self, *args, **kwargs):
        super(NationalIdForm, self).__init__(*args, **kwargs)
        self.fields['national_id'].error_messages = {
            "required": u"Please introduce your National ID number.",
            "invalid": u"Please introduce a valid National ID number.",
            "unique": u"An user with this Nationl ID number already exists.",
        }

    class Meta(object):
        model = NationalId
        fields = ('national_id',)
