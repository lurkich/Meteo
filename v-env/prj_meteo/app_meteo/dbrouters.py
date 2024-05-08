
class DbRouter(object):
    """
    A router to control all database operations on models in the auth application.
    """


    def db_for_read(self, model, **hints):
        """
        Attempts to read TempData models go to MyDataDB database.
        """
        if model._meta.db_table == 'weather_outdoor' or \
           model._meta.db_table == 'weather_indoor' or \
           model._meta.db_table == 'weather_serre':
           return 'tempcollect'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write TempData models go to the MyDataDB database.
        """
        if model._meta.db_table == 'weather_outdoor' or \
           model._meta.db_table == 'weather_indoor' or \
           model._meta.db_table == 'weather_serre':
           return 'tempcollect'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Do not allow relations involving the MyDataDB database
        """
        if obj1._meta.db_table == 'weather_outdoor' or \
           obj2._meta.db_table == 'weather_outdoor' or \
           obj1._meta.db_table == 'weather_indoor' or \
           obj2._meta.db_table == 'weather_indoor' or \
           obj1._meta.db_table == 'weather_serre' or \
           obj2._meta.db_table == 'weather_serre':
           return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Do not allow migrations on the MyDataDB database
        """
        if app_label == 'weather_outdoor' or \
           app_label == 'weather_indoor' or \
           app_label == 'weather_serre': 
           return False
        return True

