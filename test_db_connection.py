import psycopg2

try:
    connection = psycopg2.connect(
        user="postgres",
        password="891ea6f1fe7d3b49fd23",
        host="easypanel.singularmodel.com.br",
        port="54327",
        database="singular",
        sslmode="disable"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record, "\n")
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if 'connection' in locals() and connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")