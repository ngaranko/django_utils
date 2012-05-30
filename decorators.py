#django_utils/decorators.py

try:
    import json
except ImportError:
    # Python 2.5 fallback
    import simplejson as json

from django.shortcuts import render
from django.http import HttpResponse
from functools import wraps

def templated(template):
    """Templating decorator
    @param template string, template name, passed to django's render function

    Decorated function result will be processed as:
    - Dictionary: will be passed as context into render
    - None: will be converted into empty dictionary and passed to render
    - Any other case: result will be passed as output
    """
    def decorated(f):
        @wraps(f)
        def rendered(request, *args, **kwargs):
            _tpl = template
            result = f(request, *args, **kwargs)

            if result is None:
                # Function returns nothing, convert into dict
                result = {}

            elif not isinstance(result, dict):
                # Any other case, simply return result
                return result

            # Render template
            return render(request, _tpl, result)
        return rendered
    return decorated

def pdfed(template, filename=None):
    """PDF output decorator, uses pisa to generate pdf
    @param template string, template name, to be rendered as PDF
    @param filename string/None, final filename, may be None

    Decorated function result will be processed as:
    - Dictionary: will be passed as context into render
    - None: will be converted into empty dictionary and passed to render
    - Any other case: result will be passed as output
    """
    def decorated(f):
        @wraps(f)
        def rendered(*args, **kwargs):
            _tpl = template
            result = f(*args, **kwargs)

            if result is None:
                # Function returns nothing, convert into dict
                result = {}
            elif not isinstance(result, dict):
                # Any other case, simply return result
                return result

            # Render pdf, using multipage_pdf function from django-utils package
            from django_utils.pdf import multipage_pdf
            return multipage_pdf([('index', _tpl, result),], filename)

        return rendered
    return decorated

def jsoned(f):
    """Jsoned decorator

    Decorated function result will be processed as:
    - Dictionary: will be passed as context into render
    - String/Unicode: will be passed as 'status' in response {'status': %(result)}
    - None: will be converted into empty dictionary and passed to render
    - Any other case: result will be passed as output
    """
    @wraps(f)
    def rendered(*args, **kwargs):
        result = f(*args, **kwargs)
        if result is None:
            # Function returns nothing, convert into dict
            result = {}

        elif isinstance(result, basestring):
            # Function returns string, pass it as status value
            result = {'status': result}

        elif not isinstance(result, dict):
            # Any other case, simply return result
            return result

        return HttpResponse(json.dumps(result))
    return rendered

