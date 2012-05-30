#django-utils/pdf.py

from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
import ho.pisa as pisa
import cStringIO as StringIO
import cgi

def multipage_pdf(pages, filename=None):
    """Produces PDF with mutiple pages

    Arguments:
    pages -- list of tuples, each tuple contains 3 items:
        1. Page identifier,
        2. Template name
        3. Context, is a dict, used to render page

        Example:
        ('cover', 'test/cover.html', {"name": "Test cover page"})
    """

    _next_page = "<div>\n<pdf:nextpage />\n</div>"
    html = ''

    _templates = {}

    for page_name, template, context in pages:
        if template not in _templates:  # Get template
            _templates[template] = get_template(template)

        _page_context = Context(context)

        html = '%(html)s%(next_page)s%(template)s' % {
            'html': html,
            'next_page': _next_page if not html == '' else '',
            'template': _templates[template].render(_page_context)
        }

    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(StringIO.StringIO(
        html.encode("UTF-8")), result)

    # Check if pdf generation failed
    if pdf.err:
        raise Exception('Error while generating PDF, %s' % pdf.err)

    response = HttpResponse(result.getvalue(), \
             mimetype='application/pdf')

    if not filename is None:
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

