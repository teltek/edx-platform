# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.utils.translation import get_language_from_request

from certificates.api import get_active_web_certificate
from lms.djangoapps.certificates.models import CertificateTemplate, GeneratedCertificate
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore
from openedx.core.djangoapps.models.course_details import CourseDetails
from extrainfo.models import NationalId

from io import BytesIO
from PIL import Image
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4, landscape
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

    def __init__(self, verify_uuid, course_id, user_id):
        """
        Generates certificate in PDF format.
        """
        self.verify_uuid = verify_uuid
        self.course_id = course_id
        self.user_id = user_id
        self.pdf = None
        self.margin = 15 * mm
        self.page_width = 297 * mm
        self.page_height = 210 * mm

        self.min_clearance = 3 * mm
        self.second_page_available_height = ''
        self.second_page_start_y_pos = ''
        self.first_page_available_height = ''

        self.logo_uvigo = "/edx/app/edxapp/themes/xenero-microsite/lms/static/images/logouniversidadenegro.png"
        self.logo_xunta = "/edx/app/edxapp/themes/xenero-microsite/lms/static/images/logoxuntasmall.png"
        self.logo_pacto = "/edx/app/edxapp/themes/xenero-microsite/lms/static/images/logopactonegro.png"
        self.logo_ministerio = "/edx/app/edxapp/themes/xenero-microsite/lms/static/images/logoministerio.png"
        self.logo_xacobeo = "/edx/app/edxapp/themes/xenero-microsite/lms/static/images/xacobeo-positivo.png"
        self.signature = "/edx/app/edxapp/themes/xenero-microsite/lms/static/images/firma.png"
        self.signature_2 = "/edx/app/edxapp/themes/xenero-microsite/lms/static/images/firma_agueda.png"
        self.brand_logo_height = 12 * mm
        self.cobrand_logo_height = 12 * mm
        self.signature_height = 280 * mm

        self.signer_fullname = "Manuel Ramos Cabrer"
        self.signer_2_fullname = "Agueda Gómez Suárez"

        self.font_file = "/edx/app/edxapp/themes/xenero-microsite/lms/static/fonts/Roboto-Light.ttf"
        self.font_bold_file = "/edx/app/edxapp/themes/xenero-microsite/lms/static/fonts/Roboto-Black.ttf"


    def generate_pdf(self, file_buffer):
        """
        Generates PDF file with Certificate
        """
        try:
            course_key = CourseKey.from_string(self.course_id)
            course = modulestore().get_course(course_key)
            active_configuration = get_active_web_certificate(course)
            self.pdf = Canvas(file_buffer, pagesize=landscape(A4))
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
        vertical_padding_from_border = 5 * mm
        img_y_pos = self.page_height - (
                self.margin + vertical_padding_from_border + min(self.cobrand_logo_height, self.brand_logo_height)
        )
        # Left aligned brand logo
        if self.logo_uvigo:
            logo_img = self.load_image(self.logo_uvigo)
            if logo_img:
                img_width = float(logo_img.size[0] + 3 * mm) / (float(logo_img.size[1] + 3 * mm) / self.brand_logo_height)
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
        logo_xacobeo = self.load_image(self.logo_xacobeo)
        logo_xunta = self.load_image(self.logo_xunta)
        logo_pacto = self.load_image(self.logo_pacto)
        logo_ministerio = self.load_image(self.logo_ministerio)

        img_width = float(logo_xacobeo.size[0]) / (float(logo_xacobeo.size[1]) / self.cobrand_logo_height)
        self.pdf.drawImage(
            logo_xacobeo.filename,
            self.page_width - (horizontal_padding_from_border + img_width),
            img_y_pos,
            img_width,
            self.cobrand_logo_height,
            mask='auto',
            preserveAspectRatio=True,
        )
        img_width = float(logo_ministerio.size[0]) / (float(logo_ministerio.size[1]) / self.cobrand_logo_height)
        self.pdf.drawImage(
            logo_ministerio.filename,
            self.page_width - (horizontal_padding_from_border + img_width + 15 * mm),
            img_y_pos,
            img_width,
            self.cobrand_logo_height,
            mask='auto',
            preserveAspectRatio=True,
        )
        img_width = float(logo_xunta.size[0]) / (float(logo_xunta.size[1]) / self.cobrand_logo_height)
        self.pdf.drawImage(
            logo_xunta.filename,
            self.page_width - (horizontal_padding_from_border + img_width + 75 * mm),
            img_y_pos,
            img_width,
            self.cobrand_logo_height,
            mask='auto',
            preserveAspectRatio=True,
        )
        img_width = float(logo_pacto.size[0]) / (float(logo_pacto.size[1]) / self.cobrand_logo_height)
        self.pdf.drawImage(
            logo_pacto.filename,
            self.page_width - (horizontal_padding_from_border + img_width + 90 * mm),
            img_y_pos,
            img_width,
            self.cobrand_logo_height,
            mask='auto',
            preserveAspectRatio=True,
        )
            
        # Signature image
        y_pos = self.page_height - (self.margin + vertical_padding_from_border + self.signature_height)
        y_pos = -85 * mm
        if self.signature:
            rector_sign_img = self.load_image(self.signature)
            if rector_sign_img:
                img_width = float(rector_sign_img.size[0]) / (float(rector_sign_img.size[1]) / self.cobrand_logo_height)
                self.pdf.drawImage(
                    rector_sign_img.filename,
                    horizontal_padding_from_border + img_width - 5 * mm,
                    y_pos - 8 * mm,
                    img_width + 10 * mm,
                    self.signature_height + 10 * mm,
                    mask='auto',
                    preserveAspectRatio=True,
                )
        if self.signature_2:
            signature_2 = self.load_image(self.signature_2)
            if signature_2:
                img_width = float(signature_2.size[0]) / (float(signature_2.size[1]) / self.cobrand_logo_height)
                self.pdf.drawImage(
                    signature_2.filename,
                    horizontal_padding_from_border + img_width + 45 * mm,
                    y_pos - 8 * mm,
                    img_width + 10 * mm,
                    self.signature_height + 10 * mm,
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
        course_effort = course.effort if course.effort else 15
        course_credits_field = active_configuration.get('course_credits', 1.0)
        course_credits = re.findall('\d+', str(course_credits_field))
        course_credits = course_credits[0]
        certificate_id_url = settings.LMS_ROOT_URL + '/certificates/' + self.verify_uuid

        pdfmetrics.registerFont(TTFont('Roboto', self.font_file))
        pdfmetrics.registerFont(TTFont('Roboto-bold', self.font_bold_file))
        pdfmetrics.registerFontFamily('Roboto', normal='Roboto', bold='Roboto-bold')
        self.pdf.setFont('Roboto', 18)

        WIDTH = 297  # width in mm (A4)
        HEIGHT = 210  # hight in mm (A4)
        LEFT_INDENT = 49  # mm from the left side to write the text
        RIGHT_INDENT = 49  # mm from the right side for the CERTIFICATE


        try: 
            student_national_id = NationalId.objects.get(user=user.id).get_national_id()
        except NationalId.DoesNotExist:
            if preview_mode:
                national_id = "123456789-AA"
                return national_id
            raise
        
        if student_national_id:
            paragraph_text_gal = '{horizontal}{breakline}' \
                                 'Dona/Don {strong_start}{student_name}{strong_end} con DNI {strong_start}{student_national_id}{strong_end} ' \
                                 'completou satisfactoriamente o curso {course_title} ({course_effort}) ' \
                                 'do ITINERARIO FORMATIVO virtual en xénero, organizado pola Unidade de Igualdade '\
                                'e a Vicerreitoría de Ordenación Académica e Profesorado da Universidade de Vigo, '\
                                'en modalidade virtual, do'.format(
                                    student_name=user_fullname.upper(),
                                    student_national_id=student_national_id,
                                    course_title=course_name,
                                    course_effort=course_effort,
                                    strong_start="<strong>",
                                    strong_end="</strong>",
                                    horizontal="<hr>",
                                    breakline="<br/><br/>",
                                )
            paragraph_text_esp = 'Doña/Don {strong_start}{student_name}{strong_end} con DNI {strong_start}{student_national_id}{strong_end} ' \
                                    'completó satisfactoriamente el curso {course_title} ({course_effort}) ' \
                                    'del ITINERARIO FORMATIVO virtual en género, organizado por la Unidad de Igualdade '\
                                    'e a Vicerreitoría de Ordenación Académica e Profesorado da Universidade de Vigo, '\
                                    'en modalidade virtual, do'.format(
                                    student_name=user_fullname.upper(),
                                    student_national_id=student_national_id,
                                    course_title=course_name,
                                    course_effort=course_effort,
                                    strong_start="<strong>",
                                    strong_end="</strong>",
                                    breakline="<br/><br/>",
                                )

        else:
            paragraph_text = (_(u'The Rector of the National University of Distance Education,' \
                                '{breakline}considering that{breakline}{breakline}' \
                                '{studentstyle_start}{student_name}{studentstyle_end}{breakline}{breakline}' \
                                'has successfully finished the UNED Abierta course')).format(
                studentstyle_start="<font size=24 color=#c49838>",
                studentstyle_end="</font>",
                student_name=user_fullname.upper(),
                breakline="<br/><br/>",
            )
        style = ParagraphStyle('paragraph', alignment=TA_JUSTIFY, fontSize=12, fontName="Roboto", leading=15)
        paragraph = Paragraph(paragraph_text_gal, style)
        paragraph.wrapOn(self.pdf, 100 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 30 * mm, 100 * mm, TA_LEFT)

        paragraph = Paragraph(paragraph_text_esp, style)
        paragraph.wrapOn(self.pdf, 100 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 150 * mm, 100 * mm, TA_LEFT)

        according_text = (_(u'{date}')).format(
            date=date
        )
        style = ParagraphStyle('according', alignment=TA_LEFT, fontSize=12, fontName="Roboto", leading=10)
        paragraph = Paragraph(according_text, style)
        paragraph.wrapOn(self.pdf, 100 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 30 * mm, 90 * mm, TA_CENTER)

        paragraph.wrapOn(self.pdf, 100 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 150 * mm, 90 * mm, TA_CENTER)

        rector_title = (_(u'{strong_start}Conforme{strong_end}')).format(
            strong_start="<strong>",
            strong_end="</strong>"
        )

        style = ParagraphStyle('rectortitle', alignment=TA_LEFT, fontSize=12, fontName="Roboto")
        paragraph = Paragraph(rector_title, style)
        paragraph.wrapOn(self.pdf, 160 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 30 * mm, 70 * mm, TA_LEFT)

        if self.signer_fullname:
            rector_name = ('{strong_start}{signer_fullname}{strong_end}{breakline} ' \
                           '{font_start}Universidade de Vigo{font_end}').format(
                               strong_start="<strong>",
                               signer_fullname=self.signer_fullname,
                               strong_end="</strong>",
                               font_start="<font size=8>",
                               font_end="</font>",
                               breakline="<br/>"
                           )

            style = ParagraphStyle('rectorname', alignment=TA_CENTER, fontSize=12, fontName="Roboto")
            paragraph = Paragraph(rector_name, style)
            paragraph.wrapOn(self.pdf, 60 * mm, HEIGHT * mm - 10 * mm)
            paragraph.drawOn(self.pdf, 20 * mm, 30 * mm, TA_LEFT)
            
        if self.signer_2_fullname:
            rector_name = ('{strong_start}{signer_2_fullname}{strong_end}{breakline} ' \
                           '{font_start}Universidade de Vigo{font_end}').format(
                               strong_start="<strong>",
                               signer_2_fullname=self.signer_2_fullname,
                               strong_end="</strong>",
                               font_start="<font size=8>",
                               font_end="</font>",
                               breakline="<br/>"
                           )

            style = ParagraphStyle('rectorname', alignment=TA_CENTER, fontSize=12, fontName="Roboto")
            paragraph = Paragraph(rector_name, style)
            paragraph.wrapOn(self.pdf, 160 * mm, HEIGHT * mm - 10 * mm)
            paragraph.drawOn(self.pdf, 20 * mm, 30 * mm, TA_LEFT)

        footer = (_(u'The authenticity of this document, ' \
                    'as well as its validity and validity, can be checked through the ' \
                    'following URL: ' \
                    '{link_start}{cert_url}{link_end}{breakline}')).format(
            fontsize_start="<font size=10>",
            fontsize_end="</font>",
            fontcolor_start="<font color=#00533f>",
            fontcolor_end="</font>",
            breakline="<br/>",
            course_effort=course_effort,
            link_start='<font color=#0000EE><u><a href="' + certificate_id_url + '">',
            link_end='</a></u></font>',
            cert_url=certificate_id_url
        )

        style = ParagraphStyle('footer', alignment=TA_LEFT, fontSize=8, fontName="Roboto")
        paragraph = Paragraph(footer, style)
        paragraph.wrapOn(self.pdf, 100 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 30 * mm, 10 * mm, TA_LEFT)

        footer_esp = (_(u'The authenticity of this document, ' \
                    'as well as its validity and validity, can be checked through the ' \
                    'following URL: ' \
                    '{link_start}{cert_url}{link_end}{breakline}')).format(
            fontsize_start="<font size=10>",
            fontsize_end="</font>",
            fontcolor_start="<font color=#00533f>",
            fontcolor_end="</font>",
            breakline="<br/>",
            course_effort=course_effort,
            link_start='<font color=#0000EE><u><a href="' + certificate_id_url + '">',
            link_end='</a></u></font>',
            cert_url=certificate_id_url
        )

        style = ParagraphStyle('footer_esp', alignment=TA_LEFT, fontSize=8, fontName="Roboto")
        paragraph = Paragraph(footer, style)
        paragraph.wrapOn(self.pdf, 100 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 150 * mm, 10 * mm, TA_LEFT)


        return y_pos


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
