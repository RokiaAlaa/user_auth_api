# Notes: 
1- to try the Sanctions Screening Service (below), run this once to load the list:
   docker-compose exec web python manage.py sync_sdn
   After that it updates automatically every day, no need to run it again.

2- consumer may fail its first connection attempt while RabbitMQ is still starting up, but recovers automatically via restart: on-failure