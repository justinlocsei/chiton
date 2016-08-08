import os

from django.core.wsgi import get_wsgi_application
import newrelic.agent
from raven.contrib.django.raven_compat.middleware.wsgi import Sentry


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chiton.settings')

newrelic.agent.initialize(os.environ['NEW_RELIC_CONFIG_FILE'])

application = Sentry(newrelic.agent.WSGIApplicationWrapper(get_wsgi_application()))
