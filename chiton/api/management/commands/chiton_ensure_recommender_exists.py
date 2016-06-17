from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

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
        token = options['token']
        username = options['username']

        # Ensure that the group exists
        try:
            group = Group.objects.get(name=GROUP_NAME)
        except Group.DoesNotExist:
            group = Group.objects.create(name=GROUP_NAME)
            self.stdout.write('Created the %s group' % group.name)

        # Ensure that the group has the correct create permissions
        for model_class in CREATE_MODELS:
            content_type = ContentType.objects.get_for_model(model_class)
            create_permission = Permission.objects.get(content_type=content_type, codename__startswith='add_')
            try:
                group.permissions.get(pk=create_permission.pk)
            except ObjectDoesNotExist:
                group.permissions.add(create_permission)
                self.stdout.write('Allowed members of the %s group to create %s' % (group.name, model_class._meta.verbose_name_plural))

        # Ensure that the user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username)
            self.stdout.write('Added user %s' % username)

        # Ensure that the user is a member of the group
        try:
            user.groups.get(pk=group.pk)
        except ObjectDoesNotExist:
            user.groups.add(group)
            self.stdout.write('Added %s to the %s group' % (username, group.name))

        # Ensure that the user has the given token
        update_token = False
        try:
            auth_token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            update_token = True
        else:
            if auth_token.key != token:
                auth_token.delete()
                update_token = True
        if update_token:
            Token.objects.create(user=user, key=token)
            self.stdout.write('Updated token for %s' % username)
