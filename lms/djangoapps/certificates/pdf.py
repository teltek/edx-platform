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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
        y_pos = self.add_text(y_pos)

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


    def add_text(self, y_pos):
        first_line = _('NATIONAL UNIVERSITY OF DISTANCE EDUCATION')
        paragraph = (_('The Rector of the National University of Distance Education, considering that {student_name} with National Identity Number: {student_national_id} has successfully finished the UNED Abierta course {course_title} According to the program on the back of this document, issues the present CERTIFICATE OF USE')).format(student_name="Student Name", student_national_id="123456789X", course_title="Title of the course")
        date_cert = _('26th July 2018')
        rector_title = _('The Rector of the UNED,')
        rector_name = 'Alejandro Tiana Ferrer'
        credits_number_line = (_('Credits number: {course_credits} ETCS')).format(course_credits=1.0)
        course_effort_line = (_('Hours number: {course_effort} hours')).format(course_effort=25)
        law_line = _('This degree is given as suitable of UNED and it does not have the official nature established in number 30 of the Organic Law 4/2007 that modifies the article 34 of Organic Law 6/2001 of Universities')
        auth_line = (_('* The authenticity of this document, as well as its validity and validity, can be checked through the following URL: {cert_url}')).format(cert_url='https://example.com')

        id_label = 'testing-label-id'
        item_id = 'testing-item-id'
        title = first_line

        log.error('Available fonts: {0}'.format(self.pdf.getAvailableFonts()))

        # pdfmetrics.registerFont(TTFont('Fontana-Semibold', '../../static/certificates/fonts/Fontana/Fontana-ND-Cc-OsF-Semibold.otf'))
        # self.pdf.setFont('Fontana-Semibold', 18)

        vertical_padding = 5 * mm
        horizontal_padding_from_border = self.margin + 18 * mm
        font_size = 18
        self.pdf.setFontSize(font_size)
        self.pdf.drawString(horizontal_padding_from_border, y_pos - vertical_padding - font_size / 2, title)
        y_pos = y_pos - vertical_padding - font_size / 2 - self.min_clearance

        horizontal_padding_from_border = self.margin + 11 * mm
        font_size = 12
        self.pdf.setFontSize(font_size)
        y_pos = y_pos - font_size / 2 - vertical_padding
        # Draw Order/Invoice No.
        self.pdf.drawString(horizontal_padding_from_border, y_pos,
                            _(u'{id_label} # {item_id}').format(id_label=id_label, item_id=item_id))
        y_pos = y_pos - font_size / 2 - vertical_padding
        # Draw Date
        # self.pdf.drawString(
        #     horizontal_padding_from_border, y_pos, _(u'Date: {date}').format(date=self.date)
        # )

        y_pos = y_pos - self.min_clearance

        return y_pos

