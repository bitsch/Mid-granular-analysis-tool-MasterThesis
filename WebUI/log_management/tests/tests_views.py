"""Log Management Views Tests
"""

from django.test import TestCase, Client
from django.urls import reverse

# Create your views' tests here.
class TestViews(TestCase):
    """
    Log Management views test class
    """

    def setUp(self):
        """Setups defaults before each test"""
        self.client = Client()
        self.index_url = reverse("index")
        self.set_log_url = reverse("set_log", args=["some-log.csv"])

    def test_index_GET_returns_index_page(self):
        """Index > GET should return the index page"""
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "log_management/index.html", "base.html")

    def test_index_POST_redirects_to_index(self):
        """Index > POST should REDIRECT to the index page"""
        response = self.client.post(self.index_url, {"uploadButton": "uploadButton"})
        self.assertEqual(response.status_code, 302)

    # The following is commented out not to delete the existing log
    # def test_index_POST_deletes_the_specified_log(self):
    #     '''Index > POST should delete the specified log'''
    #     response = self.client.post(self.index_url, {
    #         'deleteButton': 'deleteButton',
    #         'log_list': 'log.csv'
    #     })

    #     self.assertEqual(response.status_code, 200)

    def test_index_POST_redirects_when_no_log_name(self):
        """Index > POST delete with no log name specified should redirect to index page"""
        response = self.client.post(self.index_url, {"deleteButton": "deleteButton"})
        self.assertEqual(response.status_code, 302)

    def test_index_POST_set_log_and_redirects(self):
        """Index > POST set log should redirect to the set log view"""
        response = self.client.post(
            self.index_url, {"setButton": "setButton", "log_list": "log.csv"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "setlog/log.csv/")

    def test_set_log_POST_set_the_current_log_and_redirects(self):
        """Index > POST set current log should succeed and redirect to index page"""
        response = self.client.post(
            self.set_log_url,
            {
                "logName": "log.csv",
                "caseId": "case_id",
                "caseConcept": "case_concept",
                "inlineRadioOptions": "noninterval",
                "timestamp": "timestampt_column",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/logmanagement/")
