import json
import logging
import requests
import urllib2
import itertools
import MySQLdb
import copy
import re

from pkg_resources import resource_string
from lxml import html, etree
from urlparse import urlparse

from django.http import Http404
from django.conf import settings
from django.utils.translation import ugettext as _

from xmodule.x_module import XModule, DescriptorSystem
from xmodule.modulestore import Location
from xmodule.raw_module import RawDescriptor
from xmodule.editing_module import MetadataOnlyEditingDescriptor, TabsEditingDescriptor
from xmodule.xml_module import is_pointer_tag, name_to_pathname, deserialize_field
from xblock.fields import Scope, String, List, ScopeIds, Dict, Float, Integer, Boolean
from xmodule.fields import RelativeTime

from xmodule.modulestore.inheritance import InheritanceKeyValueStore
from xblock.runtime import DbModel, KvsFieldData

from django.http import HttpRequest


########################
### Global variables ###
########################

log = logging.getLogger(__name__)
WRONG_URL = "Wrong URL"
CHECK_URL = "Check the URL. Remember, videos from these valid sources: tv.campusdomar.es or tv.uvigo.es"


class PumukitFields(object):
    """
    PUMUKIT FIELDS
    Fields for `PumukitModule` and `PumukitDescriptor`.
    """
    display_name = String(
        display_name="Display Name",
        help="Display name for this module in case the source video doesn't have any.",
        default="Pumukit",
        scope=Scope.settings
    )
    video_url = String(
        display_name="Video URL",
        help="URL of the video. Valid sources: tv.uvigo.es or tv.campusdomar.es",
        default="https://tv.uvigo.es/es/video/mm/23759.html",
        scope=Scope.settings
    )
    video_list = String(
        display_name="Video List",
        help="Available videos for the authors of this course.",
        scope=Scope.settings,
        default="Anything",
        values=[]
    )
    alternative_video_title = String(
        display_name="Alternative Video Title",
        help="Display name for this video in case the source video doesn't have any or in case additional text is required by the author.",
        default="Pumukit",
        scope=Scope.settings
    ) 
    previous_url = String(
        display_name="Previous URL",
        help="Getting track of changes of the url",
        default="https://tv.uvigo.es/es/video/mm/23759.html",
        scope=Scope.settings
    ) 
    previous_title = String(
        display_name="Previous title",
        help="Getting track of changes in the title",
        default="Pumukit",
        scope=Scope.settings
    )
    previous_iframe = String(
        display_name="Previous iframe",
        help="Auxiliar field for changes in title",
        default="<iframe src=\"https://tv.uvigo.es/video/iframe/width/740/height/420/id/23759\?image\=EDX\" style=\"border:0px #FFFFFF none;\" name=\"Pumukit - Media Player\" scrolling=\"no\" frameborder=\"1\" marginheight=\"0px\" marginwidth=\"0px\"  allowfullscreen webkitallowfullscreen height=\"420\" width=\"740\"></iframe>",
        scope=Scope.settings
    )
    available_videos = List(
        display_name="Available videos",
        help="Available videos for this course",
        default=[],
        scope=Scope.settings
    )
    previous_list = String(
        display_name="Previous list",
        help="Auxiliary field for changes in list",
        default="Anything",
        scope=Scope.settings
    )
    show_video_title = String(
        display_name="Show Video Title",
        help="Title of the video to show",
        default="Pumukit",
        scope=Scope.settings
    )
    show_video_iframe = String(
        display_name="Show Video Iframe",
        help="Iframe of the video to show",
        default="<iframe src=\"https://tv.uvigo.es/video/iframe/width/740/height/420/id/23759?image=EDX\" style=\"border:0px #FFFFFF none;\" name=\"Pumukit - Media Player\" scrolling=\"no\" frameborder=\"1\" marginheight=\"0px\" marginwidth=\"0px\"  allowfullscreen webkitallowfullscreen height=\"420\" width=\"740\"></iframe>",
        scope=Scope.settings
    )
    two_titles = Boolean(
        display_name="Two Titles",
        help="Showing an alternative subtitle or not",
        default="",
        scope=Scope.settings
    )


class PumukitModule(PumukitFields, XModule):
    """
    PUMUKIT MODULE
    """
    icon_class = 'video'
    js = {
        'coffee': [
            resource_string(__name__, 'js/src/pumukit/display.coffee')
        ]
    }
    css = {'scss': [resource_string(__name__, 'css/pumukit/display.scss')]}
    js_module_name = "Pumukit"


    def handle_ajax(self, dispatch, data):
        """
        handle ajax
        """
        log.info(u'GET {}'.format(data))
        log.info(u'DISPATCH {}'.format(dispatch))
        accepted_keys = []
        if dispatch == 'save_user_state':
            for key in data:
                if hasattr(self, key) and key in accepted_keys:
                    value = data[key]
                setattr(self, key, value)
            return json.dumps({'success': True})      
        log.debug(u"GET {0}".format(data))
        log.debug(u"DISPATCH {0}".format(dispatch))
        return ({'success': True})

    
    def get_html(self):
        """
        Get the HTML representation for showing this module
        """
        return self.system.render_template('pumukit.html', {
            'display_name': self.display_name_with_default,
            'id': self.location.html_id(),
            'video_title': self.show_video_title,
            'video_iframe': self.show_video_iframe,
            'alternative_video_title': self.alternative_video_title,
            'two_titles': self.two_titles
        })



class PumukitDescriptor(PumukitFields, MetadataOnlyEditingDescriptor, RawDescriptor):
    """
    PUMUKIT DESCRIPTOR
    """
    module_class = PumukitModule
    
    def __init__(self, *args, **kwargs):
        """
        Initialize an instance of this module
        """
        super(PumukitDescriptor, self).__init__(*args, **kwargs)

        self.available_videos = self.get_available_videos(self.location.html_id())

        editable_fields = self.editable_metadata_fields


    def editor_saved(self, user, old_metadata, old_content):
        """
        Called when clicking save on Editor in Studio.
        """
        if self.video_url not in self.previous_url:
            output = self.check_for_changes()


    def check_for_changes(self):
        """
        Check if there was any change in settings
        """
        video_title = self.previous_title
        video_iframe = self.previous_iframe

        vid_title = "Select video"
        vid_values = self.available_videos

        for vid_value in vid_values:
            if self.video_list in vid_value.get('value'):
                vid_title = vid_value.get('display_name')
                break

        if "tv.uvigo.es/" in self.video_url or "tv.campusdomar.es/" in self.video_url:
            video_url_value = self.video_url
            m = re.match('^(.*?) src="http://(.*?)"(.*?)$', video_url_value)
            if m is not None:
                video_url_value = '{} src="https://{}"{}'.format(*m.groups())
                self.video_url = video_url_value

        if self.video_url not in self.previous_url:
            try:
                video_player = self.get_video_iframe(self.video_url)
                self.show_video_iframe = video_player.get('value')
                if video_player.get('display_name'):
                    self.show_video_title = video_player.get('display_name')
                else:
                    self.show_video_title = "Pumukit"
            except Exception as exc:
                log.info(u'There was an error in trying to get Pumukit url: {}'.format(exc))
            self.previous_title = self.show_video_title
            self.previous_iframe = self.show_video_iframe
            self.previous_url = self.video_url 
        elif "Select video" not in vid_title and "No available videos" not in vid_title and self.previous_list not in self.video_list:
            # Selected video from the list of available videos
            self.show_video_iframe = self.video_list
            if vid_title:
                self.show_video_title = vid_title
            else:
                self.show_video_title = "Pumukit"
            self.previous_title = self.show_video_title
            self.previous_iframe = self.show_video_iframe
            self.previous_list = self.video_list     
        if self.alternative_video_title and ("Pumukit" not in self.alternative_video_title):
            self.two_titles = True
        else:
            self.two_titles = False
        return "output"


    def get_video_iframe(self, url):
        """
        Get the iframe for showing a video
        """
        vid_title = WRONG_URL
        vid_value = CHECK_URL

        html_object = html.parse(urllib2.urlopen(url))
        if "tv.uvigo.es/matterhorn" in url:
            input_values = html_object.xpath("//iframe[@id='mh_iframe']")
            if input_values:
                for value in input_values:
                    vid_value = html.tostring(value)
                    if "engage" in vid_value:
                        vid_title = html_object.find(".//title").text
                        vid_value = vid_value.replace('\n', '')
                        vid_value = vid_value.replace('http://', 'https://')
                        vid_value = vid_value.replace('width="1220"', 'width="960"')
                        vid_value = vid_value.replace('width:100%', 'width:960px')
                        vid_value = vid_value.replace('height:860px', 'height:900px')
                        vid_value = vid_value.replace('/engage/', '/paellaengage/')
                        m1 = re.match('^(.*?) style="(.*?)"(.*?)$', vid_value)
                        if m1 is not None:
                            vid_value = '{} style="{}-ms-zoom: 0.85;-moz-transform: scale(0.85);-moz-transform-origin: 0 0;-o-transform: scale(0.85);-o-transform-origin: 0 0;-webkit-transform: scale(0.85);-webkit-transform-origin: 0 0;"{}'.format(*m1.groups())
                        break
        elif "tv.uvigo.es/" in url:
            input_values = html_object.xpath("//input[@type='text']/@value")
            if input_values:
                for value in input_values:
                    if "iframe src" in value and "tv.uvigo.es" in value:
                        vid_title = html_object.find(".//title").text
                        vid_value = unicode(value, "utf-8")
                        vid_value = vid_value.replace('\n', '')
                        m1 = re.match('^(.*?) src="(.*?)"(.*?)$', vid_value)
                        if m1 is not None:
                            vid_value = '{} src="{}?image=EDX"{}'.format(*m1.groups())
                        vid_value = vid_value.replace('http://', 'https://')
                        vid_value = vid_value.replace('width="1220"', 'width="800"')
                        break
        elif "tv.campusdomar.es/" in url:
            input_values = html_object.xpath("//input[@type='text']/@value")
            if input_values:
                for value in input_values:
                    if "iframe src" in value and "tv.campusdomar.es" in value:
                        vid_title = html_object.find(".//title").text
                        vid_value = unicode(value, "utf-8")
                        vid_value = vid_value.replace('\n', '')
                        m1 = re.match('^(.*?) src="(.*?)"(.*?)$', vid_value)
                        if m1 is not None:
                            vid_value = '{} src="{}?autostart=false"{}'.format(*m1.groups())
                        vid_value = vid_value.replace('http://', 'https://')
                        vid_value = vid_value.replace('width="1220"', 'width="960"')
                        m2 = re.match('^(.*?) style="(.*?)"(.*?)$', vid_value)
                        if m2 is not None:
                            vid_value = '{} style="{}-ms-zoom: 0.85;-moz-transform: scale(0.85);-moz-transform-origin: 0 0;-o-transform: scale(0.85);-o-transform-origin: 0 0;-webkit-transform: scale(0.85);-webkit-transform-origin: 0 0;"{}'.format(*m2.groups())
                        break

        video_player = {
            "display_name": vid_title,
            "value": vid_value
        }
        return video_player


    def get_available_videos(self, location):
        """
        Get available videos for a course
        """
        full_list = [{"display_name": "No available videos", "value": "no available videos"}]
        return full_list


    @property
    def editable_metadata_fields(self):      
        """
        Editable medatada fields
        """             
        def jsonify_value(field, json_choice):
            """
            Jsonify value
            """
            if isinstance(json_choice, dict) and 'value' in json_choice:
                json_choice = dict(json_choice)
                json_choice['value'] = field.to_json(json_choice['value'])
            else:
                json_choice = field.to_json(json_choice)
            return json_choice

        fields = self.fields
        acceptable_fields = ['video_url', 'video_list', 'alternative_video_title']   
        metadata_fields = {}
     
        for field in fields.values():
            if field.name in acceptable_fields:
                metadata_fields[field.name] = self.runtime.get_field_provenance(self, field)
                metadata_fields[field.name]['field_name'] = field.name 
                metadata_fields[field.name]['display_name'] = field.display_name
                metadata_fields[field.name]['help'] = field.help
                metadata_fields[field.name]['value'] = field.read_json(self)

                editor_type = "Generic"
                
                values = field.values

                if isinstance(values, (tuple, list)) and len(values) > 0:
                    editor_type = "Select"
                    values = [jsonify_value(field, json_choice) for json_choice in values]
                elif isinstance(field, Integer):
                    editor_type = "Integer"
                elif isinstance(field, Float):
                    editor_type = "Float"
                elif isinstance(field, List):
                    editor_type = "List"
                elif isinstance(field, Dict):
                    editor_type = "Dict"
                elif isinstance(field, RelativeTime):
                    editor_type = "RelativeTime"                
                metadata_fields[field.name]['type'] = editor_type
                metadata_fields[field.name]['options'] = [] if values is None else values

        video_options = self.available_videos
        metadata_fields['video_list'].update({
            'type': "Select",
            'options': video_options,
            'value': video_options[0]
        })

        editable_fields = metadata_fields
        return editable_fields


    @classmethod
    def from_xml(cls, xml_data, system, id_generator):
        """
        Creates an instance of this descriptor from the supplied xml_data.
        This may be overridden by subclasses

        xml_data: A string of xml that will be translated into data and children for
            this module
        system: A DescriptorSystem for interacting with external resources
        org and course are optional strings that will be used in the generated modules
            url identifiers
        """
        xml_object = etree.fromstring(xml_data)
        url_name = xml_object.get('url_name', xml_object.get('slug'))
        block_type = 'pumukit'
        definition_id = id_generator.create_definition(block_type, url_name)
        usage_id = id_generator.create_usage(definition_id)

        if is_pointer_tag(xml_object):
            filepath = cls._format_filepath(xml_object.tag, name_to_pathname(url_name))
            xml_data = etree.tostring(cls.load_file(filepath, system.resources_fs, usage_id))

        field_data = cls._parse_pumukit_xml(xml_data)
        kvs = InheritanceKeyValueStore(initial_values=field_data)
        field_data = KvsFieldData(kvs)

        pumukit = system.construct_xblock_from_class(
            cls,
            ScopeIds(None, block_type, definition_id, usage_id),
            field_data,
        ) 

        return pumukit


    def definition_to_xml(self, resource_fs):
        """
        Returns an xml string representing this module.
        """
        xml = etree.Element('pumukit')
        xml.set('url_name', self.url_name)
        attrs = {
            'display_name': self.display_name,
            'video_url': self.video_url,
            'alternative_video_title': self.alternative_video_title,
            'video_list': self.video_list,
            'available_videos': self.available_videos,
            'previous_title': self.previous_title,
            'previous_url': self.previous_url,
            'previous_list': self.previous_list,
            'previous_iframe': self.previous_iframe,
        }

        for key, value in attrs.items():
            if value:
               # if key in self.fields and self.fields[key].is_set_on(self):
               # Less restricted for getting all the fields
               if key in self.fields:
                    xml.set(key, unicode(value))   

        return xml

  
    @classmethod
    def _parse_pumukit_xml(cls, xml_data):
        """
        Parse Pumukit fields out of xml_data. The fields are set if they are
        present in the XML.
        """
        xml = etree.fromstring(xml_data)
        field_data = {}

        for attr, value in xml.items():
            if attr in cls.metadata_to_strip + ('url_name', 'name'):
                continue
            # We export values with json.dumps
            value = deserialize_field(cls.fields[attr], value)
            field_data[attr] = value

        return field_data  
