from django.utils import autoreload
from uwsgidecorators import timer
import uwsgi


@timer(2)
def reload_code_when_changed(signal):
    """Reload uWSGI if Django detects that code has changed."""
    if autoreload.code_changed():
        uwsgi.reload()
