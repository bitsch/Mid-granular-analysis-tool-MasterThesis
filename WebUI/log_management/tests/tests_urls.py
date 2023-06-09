"""Log Management Urls Tests
"""
from django.test.testcases import SimpleTestCase
from django.urls import resolve, reverse
from log_management.views import index, set_log, get_log_info

# Create your tests here.
class TestUrls(SimpleTestCase):
    """
    Log Management urls test class
    """

    def test_index_url_is_resolved(self):
        """Tests if index url is resolved"""

        url = reverse("index")
        self.assertEqual(resolve(url).func, index, "Index view is expected")

    def test_set_log_url_is_resolved(self):
        """Tests if set_log url is resolved"""

        url = reverse("set_log", args=["some-log.csv"])
        self.assertEqual(resolve(url).func, set_log, "Setting the log view is expected")

    def test_get_log_info_url_is_resolved(self):
        """Tests if get_log_info url is resolved"""

        url = reverse("get_log_info")
        self.assertEqual(resolve(url).func, get_log_info, "Ajax log info is expected")
