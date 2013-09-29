"""
Decrease the verbosity of writing view tests.

Old way:

    self.client.get(reverse("my-view"))
    self.client.post(reverse("my-view"), data={"key": "value"})
    self.client.login("username", "password")
    self.client.get(reverse("my-other-view"))
    self.client.logout()

    self.client.post(reverse("my-other-view"), data={"key": "value"}
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response["Location"], "http://remoteserver/")

    session = self.client.session
    session["key"] = "value"
    session.save()

New way:

    self.client.get("my-view")
    self.client.post("my-view", data={"key": "value"})
    with self.login("username", "password"):
        self.client.get("my-other-view")

    self.assertRedirectsTo(response, "http://remoteserver/")

    session = self.session
    session["key"] = "value"
    session.save()

By default also patches the template loader and initiates the client session.
"""

from django.conf import settings
from django.template import Template
from django.test import TestCase
import django.template.loader
from django.utils.importlib import import_module

from model_mommy import mommy


class UserLogin(object):

    def __init__(self, testcase, user, password):
        self.testcase = testcase
        success = testcase.client.login(username=user, password=password)
        self.testcase.assertTrue(
            success,
            "login with username=%r, password=%r failed" % (user, password)
        )

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.testcase.client.logout()


class LazyTestCase(TestCase):
    patch_templates = True

    def login(self, user, password):
        return UserLogin(self, user, password)

    @property
    def session(self):
        return self.client.session

    def load_data(self):
        return

    def setUp(self):
        if getattr(self, 'patch_templates', False) and hasattr(self, 'get_template'):
            self.get_template = django.template.loader.get_template

            def get_template(*args, **kwargs):
                return Template("")
            django.template.loader.get_template = get_template

        if "django.contrib.sessions" in settings.INSTALLED_APPS:
            # Workaround for https://code.djangoproject.com/ticket/15740
            engine = import_module(settings.SESSION_ENGINE)
            store = engine.SessionStore()
            store.save()
            self.client.cookies[
                settings.SESSION_COOKIE_NAME] = store.session_key

        self.load_data()

    def tearDown(self):
        if getattr(self, 'patch_templates', False) and hasattr(self, 'get_template'):
            django.template.loader.get_template = self.get_template

    def assertRedirectsTo(self, response, url):
        """
        Assert that a response redirects to a specific url without trying to
        load the other page.
        """
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], url)

    def assertLocationEquals(self, response, url):
        """
        Assert that a response redirects to a specific url without trying to
        load the other page.
        """
        self.assertEqual(response._headers.get("location")[1], url)


class TestCaseWithUsersMixin(object):

    def make_user(self, username, password, **kwargs):
        email = "{username}@example.com".format(username=username)
        user = mommy.make(
            'auth.User', username=username, email=email, **kwargs)
        user._unecrypted_password = password
        user.set_password(password)
        user.save()
        return user
