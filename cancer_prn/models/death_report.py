from datetime import datetime, time
from django.db import models
from edc_action_item.model_mixins import ActionModelMixin
from edc_base.model_fields import IsDateEstimatedField
from edc_base.model_mixins.base_uuid_model import BaseUuidModel
from edc_base.sites.site_model_mixin import SiteModelMixin

from edc_death_report.models import (
    Cause, CauseCategory, ReasonHospitalized,
    DiagnosisCode, MedicalResponsibility)

from ..action_items import DEATH_REPORT_ACTION
from edc_protocol.validators import date_not_before_study_start
from edc_base.model_validators.date import date_not_future
from cancer_subject.models.cancer_diagnosis import OtherCharField
from edc_constants.choices import YES_NO


class DeathReport(SiteModelMixin,
                  ActionModelMixin, BaseUuidModel):

    action_name = DEATH_REPORT_ACTION

    tracking_identifier_prefix = 'DR'

    is_death_date_estimated = IsDateEstimatedField(
        verbose_name="Is date of death estimated?",
        null=True,
        blank=False,
    )
    
    death_date = models.DateField(
        verbose_name="Date of Death:",
        validators=[
            date_not_before_study_start,
            date_not_future])

    cause = models.ForeignKey(
        to=Cause,
        verbose_name=(
            'What is the primary source of cause of death information? '
            '(if multiple source of information, '
            'list one with the smallest number closest to the top of the list) '),
        on_delete=models.PROTECT)

    cause_other = OtherCharField(
        verbose_name="if other specify...",
        blank=True,
        null=True)

    death_cause = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name=(
            'Describe the major cause of death(including pertinent autopsy information '
            'if available),starting with the first noticeable illness thought to be '
            'related to death,continuing to time of death.'),
        help_text=(
            'Note: Cardiac and pulmonary arrest are not major reasons and should not '
            'be used to describe major cause'))

    cause_category = models.ForeignKey(
        to=CauseCategory,
        verbose_name=("Based on the above description, what category "
                      "best defines the major cause of death? "),
        help_text="",
        on_delete=models.PROTECT)

    cause_category_other = OtherCharField(
        verbose_name="if other specify...",
        blank=True,
        null=True)

    participant_hospitalized = models.CharField(
        max_length=3,
        choices=YES_NO,
        verbose_name="Was the participant hospitalised before death?")

    reason_hospitalized = models.ForeignKey(
        ReasonHospitalized,
        verbose_name="if yes, hospitalized, what was the primary reason for hospitalisation? ",
        help_text="",
        blank=True,
        null=True,
        on_delete=models.PROTECT)

    reason_hospitalized_other = models.TextField(
        verbose_name=("if other illness or pathogen specify or non "
                      "infectious reason, please specify below:"),
        max_length=250,
        blank=True,
        null=True)

    days_hospitalized = models.IntegerField(
        verbose_name=(
            "For how many days was the participant hospitalised during "
            "the illness immediately before death? "),
        help_text="in days",
        default=0)

    comment = models.TextField(
        max_length=500,
        verbose_name="Comments",
        blank=True,
        null=True)

    illness_duration = models.IntegerField(
        verbose_name="Duration of acute illness directly causing death   ",
        help_text="in days (If unknown enter -1)")

    perform_autopsy = models.CharField(
        max_length=3,
        choices=YES_NO,
        verbose_name="Will an autopsy be performed later  ")

    diagnosis_code = models.ForeignKey(
        DiagnosisCode,
        max_length=25,
        verbose_name="Please code the cause of death as one of the following:",
        help_text="Use diagnosis code from Diagnosis Reference Listing",
        on_delete=models.PROTECT)

    diagnosis_code_other = OtherCharField(
        verbose_name="if other specify...",
        blank=True,
        null=True)

    medical_responsibility = models.ForeignKey(
        MedicalResponsibility,
        verbose_name=(
            "Who was responsible for primary medical care of the "
            "participant during the month prior to death?"),
        help_text="",
        on_delete=models.PROTECT)

    def get_report_datetime(self):
        return datetime.combine(self.death_date, time(0, 0))

    class Meta:
        app_label = "cancer_prn"
        verbose_name = "Subject Death"
