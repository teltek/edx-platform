
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.utils.translation import get_language_from_request

from certificates.api import get_active_web_certificate
from certificates.models import CertificateTemplate, GeneratedCertificate
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore
from openedx.core.djangoapps.models.course_details import CourseDetails
from openedx.core.djangoapps.userinfo.models import NationalId

from io import BytesIO
from PIL import Image
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.platypus.tables import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from PyPDF2 import PdfFileWriter, PdfFileReader
from xmodule.assetstore.assetmgr import AssetManager
from xmodule.contentstore.content import StaticContent

import re
import datetime
import pytz
from util.date_utils import strftime_localized

log = logging.getLogger(__name__)

class PDFCertificate(object):
    """
    PDF Generation Class
    """
    def __init__(self, verify_uuid, course_id, user_id, mode):
        """
        Generates certificate in PDF format.
        """
        self.verify_uuid = verify_uuid
        self.course_id = course_id
        self.user_id = user_id
        self.mode = mode
        self.pdf = None
        self.margin = 15 * mm
        self.page_width = 210 * mm
        self.page_height = 297 * mm

        self.min_clearance = 3 * mm
        self.second_page_available_height = ''
        self.second_page_start_y_pos = ''
        self.first_page_available_height = ''

        self.logo_path = settings.FEATURES.get("PDF_LOGO_MAIN", "")
        self.cobrand_logo_path = settings.FEATURES.get("PDF_LOGO_EXTRA", "")
        self.cobrand_logo_key = "mapfre" #TODO make generic
        self.brand_logo_height = 20 * mm
        self.cobrand_logo_height = 15 * mm
        self.signature_height = 290 * mm
        self.rector_fullname = settings.FEATURES.get("PDF_RECTOR_FULLNAME", "")
        self.rector_signature = settings.FEATURES.get("PDF_RECTOR_SIGNATURE", "")

    def generate_pdf(self, file_buffer):
        """
        Generates PDF file with Certificate
        """
        try:
            course_key = CourseKey.from_string(self.course_id)
            course = modulestore().get_course(course_key)
            active_configuration = get_active_web_certificate(course)
            self.pdf = Canvas(file_buffer, pagesize=A4)
            if course and active_configuration:
                y_pos = self.draw_logos(course_key)
                y_pos = self.add_text(course, active_configuration, y_pos)
            self.pdf.showPage()
            self.pdf.save()
            output_writer = self.get_output_writer(file_buffer)
            if 'course_program_path' in active_configuration and active_configuration['course_program_path']:
                return self.add_course_program(output_writer, active_configuration['course_program_path'])
        except Exception as exception:
            log.error('Invalid cert: error generating certificate: {0}'.format(exception))
            raise exception
        
        return output_writer


    def get_output_writer(self, pdf_buffer):
        """
        Generates the output writer from the
        pdf_buffer to print the PDF
        """
        pdf_buffer.seek(0)
        new_pdf = PdfFileReader(pdf_buffer)
        output_writer = PdfFileWriter()
        page = new_pdf.getPage(0)
        output_writer.addPage(page)

        return output_writer


    def add_course_program(self, output_writer, relative_path):
        """
        Adds Course Program PDF File to the Certificate
        """
        if not relative_path:
            return output_writer
        asset_key = StaticContent.get_asset_key_from_path(self.course_id, relative_path)
        content = AssetManager.find(asset_key, as_stream=True)
        existing_pdf = PdfFileReader(content._stream)
        output_writer.appendPagesFromReader(existing_pdf)

        return output_writer

    @staticmethod
    def load_image(img_path):
        """
        Loads an image given a path. An absolute path is assumed.
        If the path points to an image file, it loads and returns the Image object, None otherwise.
        """
        try:
            img = Image.open(img_path)
        except IOError, ex:
            log.exception('Pdf unable to open the image file: %s', str(ex))
            img = None

        return img


    def draw_logos(self, course_key):
        """
        Draws logos.
        """
        horizontal_padding_from_border = self.margin + 9 * mm
        vertical_padding_from_border = 11 * mm
        img_y_pos = self.page_height - (
            self.margin + vertical_padding_from_border + min(self.cobrand_logo_height, self.brand_logo_height)
        )
        # Left aligned brand logo
        if self.logo_path:
            logo_img = self.load_image(self.logo_path)
            if logo_img:
                img_width = float(logo_img.size[0]) / (float(logo_img.size[1]) / self.brand_logo_height)
                self.pdf.drawImage(
                    logo_img.filename,
                    horizontal_padding_from_border,
                    img_y_pos,
                    img_width,
                    self.brand_logo_height,
                    mask='auto',
                    preserveAspectRatio=True,
                )

        # Right Aligned cobrand logo
        if self.add_cobrand_logo(course_key):
            cobrand_img = self.load_image(self.cobrand_logo_path)
            if cobrand_img:
                img_width = float(cobrand_img.size[0]) / (float(cobrand_img.size[1]) / self.cobrand_logo_height)
                self.pdf.drawImage(
                    cobrand_img.filename,
                    self.page_width - (horizontal_padding_from_border + img_width),
                    img_y_pos,
                    img_width,
                    self.cobrand_logo_height,
                    mask='auto',
                    preserveAspectRatio=True,
                )

        # Signature image
        y_pos = self.page_height - (self.margin + vertical_padding_from_border + self.signature_height)
        y_pos = -85 * mm
        if self.rector_signature:
            rector_sign_img = self.load_image(self.rector_signature)
            if rector_sign_img:
                img_width = float(rector_sign_img.size[0]) / (float(rector_sign_img.size[1]) / self.cobrand_logo_height)
                self.pdf.drawImage(
                    rector_sign_img.filename,
                    self.page_width - (horizontal_padding_from_border + img_width + 4 * mm),
                    y_pos,
                    img_width,
                    self.signature_height,
                    mask='auto',
                    preserveAspectRatio=True,
                )

        return img_y_pos - self.min_clearance


    def add_text(self, course, active_configuration, y_pos):
        """
        Prints all text to PDF file.
        """
        date = self._get_certificate_date()
        user = User.objects.get(id=self.user_id)
        user_fullname = user.profile.name
        course_title_from_cert = active_configuration.get('course_title', '')
        course_name = course_title_from_cert
        course_name = course_title_from_cert if course_title_from_cert else course.display_name
        course_details = CourseDetails.fetch(course.id)
        course_effort_field = course_details.effort if course_details.effort else 25
        course_effort = re.findall('\d+', str(course_effort_field))
        course_effort = course_effort[0]
        course_credits_field = active_configuration.get('course_credits', 1.0)
        course_credits = re.findall('\d+', str(course_credits_field))
        course_credits = course_credits[0]
        certificate_id_url = settings.LMS_ROOT_URL + '/certificates/' + self.verify_uuid

        pdfmetrics.registerFont(TTFont('Fontana', settings.FEATURES['PDF_FONTS_NORMAL']))
        pdfmetrics.registerFont(TTFont('Fontana-Semibold', settings.FEATURES['PDF_FONTS_SEMIBOLD']))
        pdfmetrics.registerFontFamily('Fontana', normal='Fontana', bold='Fontana-Semibold')
        self.pdf.setFont('Fontana', 18)

        WIDTH = 210  # width in mm (A4)
        HEIGHT = 297  # hight in mm (A4)
        LEFT_INDENT = 49  # mm from the left side to write the text
        RIGHT_INDENT = 49  # mm from the right side for the CERTIFICATE

        first_line = (_(u'{strong_start}NATIONAL UNIVERSITY OF DISTANCE EDUCATION{strong_end}')).format(
            strong_start="<strong>",
            strong_end="</strong>"
        )

        style = ParagraphStyle('title', alignment=TA_CENTER, fontSize=18, fontName="Fontana")
        paragraph = Paragraph(first_line, style)
        paragraph.wrapOn(self.pdf, 180 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 20 * mm, 240 * mm, TA_CENTER)
        
        paragraph_text = (_(u'The Rector of the National University of Distance Education,' \
                            '{breakline}considering that{breakline}{breakline}' \
                            '{studentstyle_start}{student_name}{studentstyle_end}{breakline}' \
                            'with National Identity Number: {student_national_id}{breakline}{breakline}' \
                            'has successfully finished the UNED Abierta course')).format(
                                studentstyle_start="<font size=20 color=#c49838>",
                                studentstyle_end="</font>",
                                student_name=user_fullname.upper(),
                                student_national_id=NationalId.get_national_id_from_user(user=user),
                                breakline="<br/><br/>",
                            )
        style = ParagraphStyle('paragraph', alignment=TA_CENTER, fontSize=12, fontName="Fontana", leading=10)
        paragraph = Paragraph(paragraph_text, style)
        paragraph.wrapOn(self.pdf, 180 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 20 * mm, 170 * mm, TA_CENTER)

        course_text = (_(u'{strong_start}{coursestyle_start}{course_title}{coursestyle_end}{strong_end}')).format(
                                coursestyle_start="<font size=24 color=#870d0d>",
                                course_title=course_name,
                                coursestyle_end="</font>",
                                strong_start="<strong>",
                                strong_end="</strong>",
        )
        style = ParagraphStyle('course', alignment=TA_CENTER, fontSize=12, fontName="Fontana", leading=24)
        paragraph = Paragraph(course_text, style)
        paragraph.wrapOn(self.pdf, 180 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 20 * mm, 135 * mm, TA_CENTER)

        according_text = (_(u'According to the program on the back of this document,' \
                            '{breakline}issues the present{breakline}{breakline}{strong_start}' \
                            '{certificatestyle_start}CERTIFICATE OF USE{certificatestyle_end}' \
                            '{strong_end}{breakline}{breakline}{fontdate_start}{date}{fontdate_end}')).format(
                                breakline="<br/><br/>",
                                certificatestyle_start="<font size=20>",
                                certificatestyle_end="</font>",
                                strong_start="<strong>",
                                strong_end="</strong>",
                                fontdate_start="<font size=8>",
                                fontdate_end="</font>",
                                date=date
                            )
        style = ParagraphStyle('according', alignment=TA_CENTER, fontSize=12, fontName="Fontana", leading=10)
        paragraph = Paragraph(according_text, style)
        paragraph.wrapOn(self.pdf, 180 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 20 * mm, 90 * mm, TA_CENTER)

        rector_title = (_(u'{color_start}The Rector of the UNED,{color_end}')).format(
            color_start="<font color=#c49838>",
            color_end="</font>"
        )

        style = ParagraphStyle('rectortitle', alignment=TA_RIGHT, fontSize=10,fontName="Fontana")
        paragraph = Paragraph(rector_title, style)
        paragraph.wrapOn(self.pdf, 160 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 20 * mm, 70 * mm, TA_RIGHT)

        if self.rector_fullname:
            rector_name = (_(u'{strong_start}{rector_fullname}{strong_end}')).format(
                strong_start="<strong>",
                rector_fullname=self.rector_fullname,
                strong_end="</strong>"
            )

            style = ParagraphStyle('rectorname', alignment=TA_RIGHT, fontSize=12, fontName="Fontana")
            paragraph = Paragraph(rector_name, style)
            paragraph.wrapOn(self.pdf, 160 * mm, HEIGHT * mm)
            paragraph.drawOn(self.pdf, 20 * mm, 50 * mm, TA_RIGHT)
            
        footer = (_(u'{fontsize_start}Hours number: {fontcolor_start}' \
                    '{course_effort}{fontcolor_end} hours{fontsize_end}{breakline}' \
                    '{fontsize_start}UNED, in agreement with the Commission for Regional Study' \
                    'Centres, Students, Employment and Culture, delegated by the Government' \
                    'Council, accredits this course as {fontcolor_start}' \
                    '{course_credits}{fontcolor_end} ECTS credit*{fontsize_end}{breakline}{breakline}' \
                    'This degree is given as suitable of {fontcolor_start}UNED{fontcolor_end}' \
                    ' and it does not have the official nature established in ' \
                    '{fontcolor_start}number 30 of the Organic Law 4/2007{fontcolor_end} ' \
                    'that modifies the {fontcolor_start}article 34 of Organic Law 6/2001 ' \
                    'of Universities{fontcolor_end}. The authenticity of this document, ' \
                    'as well as its validity and validity, can be checked through the ' \
                    '{fontcolor_start}following URL{fontcolor_end}: ' \
                    '{link_start}{cert_url}{link_end}{breakline}' \
                    '* ECTS credits: recognizable as credits for cultural university activities ' \
                    'in UNED degrees and those of universities and centers with reciprocal agreements')).format(
                        fontsize_start="<font size=10>",
                        fontsize_end="</font>",
                        fontcolor_start="<font color=#00533f>",
                        fontcolor_end="</font>",
                        course_credits=course_credits,
                        breakline="<br/>",
                        course_effort=course_effort,
                        link_start='<font color=#0000EE><u><a href="'+certificate_id_url+'">',
                        link_end='</a></u></font>',
                        cert_url=certificate_id_url
                    )

        style = ParagraphStyle('footer', alignment=TA_LEFT, fontSize=8, fontName="Fontana")
        paragraph = Paragraph(footer, style)
        paragraph.wrapOn(self.pdf, 180 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 20 * mm, 10 * mm, TA_LEFT)

        return y_pos

    def add_cobrand_logo(self, course_key):
        """
        Checks if this course has a specific template.
        TODO
        """
        if not self.cobrand_logo_path:
            return False
        if self.mode and course_key:
            template = CertificateTemplate.objects.filter(
                organization_id=None,
                course_key=course_key,
                mode=self.mode,
                is_active=True
            )
        if template and (self.cobrand_logo_key in str(template).lower() or self.cobrand_logo_key in str(course_key).lower()):
            return True
        return False

    def _get_certificate_date(self):
        try:
            course_key = CourseKey.from_string(self.course_id)
            user_certificate = GeneratedCertificate.objects.get(user=self.user_id, course_id=course_key)
            date = user_certificate.modified_date
        except Exception:
            date = datetime.datetime.now(pytz.UTC)

        return _('{month} {day}, {year}').format(
            month=strftime_localized(date, "%B"),
            day=date.day,
            year=date.year
        )
