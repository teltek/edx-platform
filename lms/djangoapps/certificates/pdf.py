import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.utils.translation import get_language_from_request

from certificates.api import get_active_web_certificate
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore
from openedx.core.djangoapps.userinfo.models import NationalId

from io import BytesIO
from PIL import Image
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
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

import datetime
import pytz


log = logging.getLogger(__name__)

class PDFCertificate(object):
    """
    PDF Generation Class
    """
    def __init__(self, verify_uuid, course_id, user_id, language='en'):
        """
        Generates certificate in PDF format.
        """
        self.verify_uuid = verify_uuid
        self.course_id = course_id
        self.user_id = user_id
        self.pdf = None
        self.margin = 15 * mm
        self.page_width = 210 * mm
        self.page_height = 297 * mm
        self.language = language

        self.min_clearance = 3 * mm
        self.second_page_available_height = ''
        self.second_page_start_y_pos = ''
        self.first_page_available_height = ''

        self.logo_path = configuration_helpers.get_value("PDF_RECEIPT_LOGO_PATH", settings.PDF_RECEIPT_LOGO_PATH)
        self.cobrand_logo_path = configuration_helpers.get_value(
            "PDF_RECEIPT_COBRAND_LOGO_PATH", settings.PDF_RECEIPT_COBRAND_LOGO_PATH
        )
        self.brand_logo_height = configuration_helpers.get_value(
            "PDF_RECEIPT_LOGO_HEIGHT_MM", settings.PDF_RECEIPT_LOGO_HEIGHT_MM
        ) * mm
        self.cobrand_logo_height = configuration_helpers.get_value(
            "PDF_RECEIPT_COBRAND_LOGO_HEIGHT_MM", settings.PDF_RECEIPT_COBRAND_LOGO_HEIGHT_MM
        ) * mm


    def generate_pdf(self, file_buffer):
        """
        Generates PDF file with Certificate
        """

        try:
            course_key = CourseKey.from_string(self.course_id)
            course = modulestore().get_course(course_key)
            active_configuration = get_active_web_certificate(course)
            self.pdf = Canvas(file_buffer, pagesize=letter)
            if course and active_configuration:
                y_pos = self.draw_logos()
                y_pos = self.add_text(course, active_configuration, y_pos)
            self.pdf.showPage()
            self.pdf.save()
            if 'course_program_path' in active_configuration:
                return self.add_course_program(file_buffer, active_configuration['course_program_path'])
        except Exception as exception:
            error_str = (
                "Invalid cert: error finding course %s. "
                "Specific error: %s"
            )
            log.error(error_str, self.course_id, str(exception))
        
        return file_buffer

    def add_course_program(self, pdf_buffer, relative_path):
        """
        Adds Course Program PDF File to the Certificate
        """
        if not relative_path:
            return pdf_buffer
        pdf_buffer.seek(0)
        new_pdf = PdfFileReader(pdf_buffer)
        asset_key = StaticContent.get_asset_key_from_path(self.course_id, relative_path)
        content = AssetManager.find(asset_key, as_stream=True)
        existing_pdf = PdfFileReader(content._stream)
        output_writer = PdfFileWriter()
        page = new_pdf.getPage(0)
        output_writer.addPage(page)
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


    def draw_logos(self):
        """
        Draws logos.
        """
        horizontal_padding_from_border = self.margin + 9 * mm
        vertical_padding_from_border = 11 * mm
        img_y_pos = self.page_height - (
            self.margin + vertical_padding_from_border + max(self.cobrand_logo_height, self.brand_logo_height)
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
                    self.cobrand_logo_height,
                    mask='auto'
                )

        # Right Aligned cobrand logo
        if self.cobrand_logo_path:
            cobrand_img = self.load_image(self.cobrand_logo_path)
            if cobrand_img:
                img_width = float(cobrand_img.size[0]) / (float(cobrand_img.size[1]) / self.cobrand_logo_height)
                self.pdf.drawImage(
                    cobrand_img.filename,
                    self.page_width - (horizontal_padding_from_border + img_width),
                    img_y_pos,
                    img_width,
                    self.cobrand_logo_height,
                    mask='auto'
                )

        return img_y_pos - self.min_clearance


    def add_text(self, course, active_configuration, y_pos):
        """
        Prints all text to PDF file.
        """
        now = datetime.datetime.now(pytz.UTC)
        user = User.objects.get(id=self.user_id)
        user_fullname = user.profile.name
        course_title_from_cert = active_configuration.get('course_title', '')
        course_name = course_title_from_cert
        course_name = course_title_from_cert if course_title_from_cert else course.display_name

        if settings.FEATURES['PDF_FONTS_EXTRA']:
            pdfmetrics.registerFont(TTFont('Fontana', settings.FEATURES['PDF_FONTS_EXTRA']))
            pdfmetrics.registerFont(TTFont('Fontana-Semibold', settings.FEATURES['PDF_FONTS_EXTRA_2']))
            pdfmetrics.registerFontFamily('Fontana', normal='Fontana', bold='Fontana-Semibold')
            self.pdf.setFont('Fontana', 18)

        first_line = (_(u'{bold_start}NATIONAL UNIVERSITY OF DISTANCE EDUCATION{bold_end}')).format(bold_start="<strong>", bold_end="</strong>")
        paragraph_text = (_('The Rector of the National University of Distance Education,' \
                            '{breakline}considering that{breakline}{breakline}' \
                            '{studentstyle_start}{student_name}{studentstyle_end}{breakline}' \
                            'with National Identity Number: {student_national_id}{breakline}{breakline}' \
                            'has successfully finished the UNED Abierta course{breakline}{breakline}' \
                            '{coursestyle_start}{course_title}{coursestyle_end}{breakline}{breakline}' \
                            'According to the program on the back of this document,' \
                            '{breakline}issues the present{breakline}' \
                            '{certificatestyle_start}CERTIFICATE OF USE{certificatestyle_end}{breakline}' \
                            '{date}')).format(
                                studentstyle_start="<font size=20 color=#c49838>",
                                studentstyle_end="</font>",
                                student_name=user_fullname,
                                student_national_id=NationalId.get_national_id_from_user(user=user),
                                coursestyle_start="<font size=20 color=#870d0d>",
                                course_title=course_name,
                                coursestyle_end="</font>",
                                breakline="<br/><br/>",
                                certificatestyle_start="<font size=18>",
                                certificatestyle_end="</font>",
                                date=now.strftime('%d %B %Y')
                            )
        rector_title = (_('{color_start}The Rector of the UNED,{color_end}')).format(color_start="<font color=#c49838>", color_end="</font>")
        rector_name = (_('{bold_start}Alejandro Tiana Ferrer{bold_end}')).format(bold_start="<b>", bold_end="</b>")
        footer = (_('Credits number: {course_credits} ETCS{breakline}Hours number: {course_effort} hours{breakline}This degree is given as suitable of UNED and it does not have the official nature established in number 30 of the Organic Law 4/2007 that modifies the article 34 of Organic Law 6/2001 of Universities{breakline}* The authenticity of this document, as well as its validity and validity, can be checked through the following URL: {cert_url}')).format(course_credits=1.0, breakline="<br/>", course_effort=25, cert_url='https://example.com')
        course_effort_line = (_('Hours number: {course_effort} hours')).format(course_effort=25)
        law_line = _('This degree is given as suitable of UNED and it does not have the official nature established in number 30 of the Organic Law 4/2007 that modifies the article 34 of Organic Law 6/2001 of Universities')
        auth_line = (_('* The authenticity of this document, as well as its validity and validity, can be checked through the following URL: {cert_url}')).format(cert_url='https://example.com')

        title = first_line

        WIDTH = 210  # width in mm (A4)
        HEIGHT = 297  # hight in mm (A4)
        LEFT_INDENT = 49  # mm from the left side to write the text
        RIGHT_INDENT = 49  # mm from the right side for the CERTIFICATE

        style = ParagraphStyle('title', alignment=TA_CENTER, fontSize=18, fontName="Fontana")
        paragraph = Paragraph(title, style)
        paragraph.wrapOn(self.pdf, 180 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 20 * mm, 240 * mm, TA_CENTER)

        style = ParagraphStyle('paragraph', alignment=TA_CENTER, fontSize=12, fontName="Fontana", leading=14)
        paragraph = Paragraph(paragraph_text, style)
        paragraph.wrapOn(self.pdf, 180 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 20 * mm, 90 * mm, TA_CENTER)

        style = ParagraphStyle('rectortitle', alignment=TA_RIGHT, fontSize=10,fontName="Fontana")
        paragraph = Paragraph(rector_title, style)
        paragraph.wrapOn(self.pdf, 180 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 20 * mm, 60 * mm, TA_RIGHT)

        style = ParagraphStyle('rectorname', alignment=TA_RIGHT, fontSize=12, fontName="Fontana")
        paragraph = Paragraph(rector_name, style)
        paragraph.wrapOn(self.pdf, 180 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 20 * mm, 50 * mm, TA_RIGHT)

        style = ParagraphStyle('footer', alignment=TA_LEFT, fontSize=8, fontName="Fontana")
        paragraph = Paragraph(footer, style)
        paragraph.wrapOn(self.pdf, 180 * mm, HEIGHT * mm)
        paragraph.drawOn(self.pdf, 20 * mm, 10 * mm, TA_LEFT)

        return y_pos

