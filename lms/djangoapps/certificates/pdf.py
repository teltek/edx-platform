import logging

from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import get_language_from_request

from certificates.api import get_active_web_certificate
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

from io import BytesIO
from PIL import Image
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.platypus.tables import Table, TableStyle

from PyPDF2 import PdfFileWriter, PdfFileReader
from xmodule.assetstore.assetmgr import AssetManager
from xmodule.contentstore.content import StaticContent

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
        self.pdf = Canvas(file_buffer, pagesize=letter)
        y_pos = self.draw_logos()

        self.pdf.showPage()
        self.pdf.save()

        try:
            course_key = CourseKey.from_string(self.course_id)
            course = modulestore().get_course(course_key)
            active_configuration = get_active_web_certificate(course)
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

