import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone

import notification.utility as notification
from user.models import CredentialApplication, User

LOGGER = logging.getLogger(__name__)


def get_application_to_be_rejected(number_of_applications=settings.DEFAULT_NUMBER_OF_APPLICATIONS_TO_REJECT):
    """
    Get all CredentialApplication that has been pending for more than
    settings.MAX_REFERENCE_VERIFICATION_DAYS_BEFORE_AUTO_REJECTION days.
    """
    today = timezone.now()
    limit = today - timezone.timedelta(days=settings.MAX_REFERENCE_VERIFICATION_DAYS_BEFORE_AUTO_REJECTION)

    # get all applications that have decision pending
    applications = CredentialApplication.objects.filter(status=0)
    # get applications with Reference Response pending
    response_applications = applications.filter(credential_review__status=30)
    # finally get applications that have been pending for more than the limit
    filtered_applications = response_applications.filter(reference_contact_datetime__lt=limit)[:number_of_applications]
    return filtered_applications


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-n", "--number", type=int, help="Number of applications to be rejected")

    def handle(self, *args, **options):
        """
        Delete all Credentialing applications whose reference checks have Awaiting Reference Response pending after
        waiting for settings.MAX_REFERENCE_VERIFICATION_DAYS_BEFORE_AUTO_REJECTION days.
        """

        # only perform auto rejection if the setting.ENABLE_CREDENTIALING_AUTO_REJECTION is True
        if not settings.ENABLE_CREDENTIALING_AUTO_REJECTION:
            LOGGER.info('Auto rejection of credentialing applications is disabled. Exiting.')
            LOGGER.warning('If this was unintentional, please set '
                           'MAX_REFERENCE_VERIFICATION_DAYS_BEFORE_AUTO_REJECTION to True in .env file.')
            return

        total_applications_to_reject = options['number'] or settings.DEFAULT_NUMBER_OF_APPLICATIONS_TO_REJECT

        # creating an instance of HttpRequest to be used in the notification utility
        request = HttpRequest()

        filtered_applications = get_application_to_be_rejected(total_applications_to_reject)

        LOGGER.info(f'{len(filtered_applications)} credentialing applications selected for rejection.'
                    f' No ref response.')
        for application in filtered_applications:
            with transaction.atomic():
                application.auto_reject(reason=CredentialApplication.AutoRejectionReason.NO_RESPONSE_FROM_REFERENCE)

                notification.process_credential_complete(request, application)
                LOGGER.info(f'Rejected ApplicationID: {application.id}. Notification sent to applicant: '
                            f'{application.get_full_name()}')
