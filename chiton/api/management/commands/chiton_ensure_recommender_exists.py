from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from chiton.api.users import bind_user_to_group, enforce_auth_token, grant_group_permission
from chiton.wintour.models import Recommendation, WardrobeProfile


# The name of the recommeders group
GROUP_NAME = 'Recommenders'

# The models that a recommender should be able to create
CREATE_MODELS = [Recommendation, WardrobeProfile]


class Command(BaseCommand):
    help = 'Ensure that a given API user exists that can generate recommendations'

    def add_arguments(self, parser):
        parser.add_argument('--token', type=str, required=True)
        parser.add_argument('--username', type=str, required=True)

    def handle(self, *arg, **options):
        group, created_group = Group.objects.get_or_create(name=GROUP_NAME)
        if created_group:
            self.stdout.write('Created the %s group' % group.name)

        for model_class in CREATE_MODELS:
            if grant_group_permission(group, model_class, add=True):
                self.stdout.write('Granted create permissions for %s' % model_class._meta.verbose_name_plural)

        user, bound_user = bind_user_to_group(options['username'], group)
        if bound_user:
            self.stdout.write('Added user %s' % user.username)

        if enforce_auth_token(user, options['token']):
            self.stdout.write('Updated the token for %s' % user.username)
