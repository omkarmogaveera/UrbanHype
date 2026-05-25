from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from django.db.backends.signals import connection_created

        def set_utc(sender, connection, **kwargs):
            if connection.vendor == 'postgresql':
                cursor = connection.connection.cursor()
                cursor.execute("SET timezone TO 'UTC'")
                cursor.close()

        connection_created.connect(set_utc)
