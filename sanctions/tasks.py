from celery import shared_task
from .services import sync_sdn_data

@shared_task
def sync_sdn_task():
    result = sync_sdn_data()

    message = (
        f"SDN sync complete. "
        f"Parsed {result['parsed_entries']}, "
        f"New entries: {result['new_entries']}, "
        f"New aliases: {result['created_aliases']}"

    )

    print(message)

    return result