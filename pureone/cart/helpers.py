from django.db import connection

def get_delivery_charge() -> float:
    with connection.cursor() as cursor:
        cursor.execute('SELECT calculate_delivery_charge()')
        result = cursor.fetchone()
    return result[0]