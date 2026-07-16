from celery import shared_task
from .services import sync_sdn_data, sync_un_data
import logging

logger = logging.getLogger(__name__)

@shared_task
def sync_sdn_task():
    result = sync_sdn_data()

    message = (
        f"SDN sync complete. "
        f"Parsed {result['parsed_entries']}, "
        f"New entries: {result['new_entries']}, "
        f"Removed entries: {result['removed_entries']}, "
        f"New aliases: {result['created_aliases']}, "
        "from OFAC list"

    )

    logger.info(message)
    return result

@shared_task
def sync_un_task():
    result = sync_un_data()

    message = (
        f"UN sync complete. "
        f"Parsed {result['parsed_entries']}, "
        f"New entries: {result['new_entries']}, "
        f"Removed entries: {result['removed_entries']}, "
        f"New aliases: {result['created_aliases']}, "
        "from UN list"

    )

    logger.info(message)
    return result