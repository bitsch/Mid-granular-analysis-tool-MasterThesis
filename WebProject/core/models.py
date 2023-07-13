from django.db import models

# Create your models here.
class SelectedLog:
    log_type = ""
    timestamp = ""
    start_timestamp = ""
    end_timestamp = ""
    lifecycle = ""

    def __init__(self, log_name, case_id, concept_name):
        self.log_name = log_name
        self.case_id = case_id
        self.concept_name = concept_name
