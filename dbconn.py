import mariadb
import dbcreds
import traceback


def open_connection():
  # Open a connection to the DB using the dbcreds.py file.
  try:
    return mariadb.connect(
        user=dbcreds.user,
        password=dbcreds.password,
        host=dbcreds.host,
        port=dbcreds.port,
        database=dbcreds.database
    )

  except:
    print("Error connecting to DB!")
    traceback.print_exc()
    return None


def close_connection(conn):
  # Close the connection to the DB using the passed argument.
  if(conn == None):
    return True
  try:
    conn.close()
    return True

  except:
    print("Error closing connection to DB!")
    traceback.print_exc()
    return False


def create_cursor(conn):
    # Create the cursor on the connection that's passed as an argument.
  try:
    return conn.cursor()
  except:
    print("Error creating cursor on the DB!")
    traceback.print_exc()
    return None


def close_cursor(cursor):
  # Close the cursor on the connection that's passed as an argument.
  if(cursor == None):
    return True
  try:
    cursor.close()
    return True

  except:
    print("Error closing cursor on DB!")
    traceback.print_exc()
    return False


def close_all(conn, cursor):
  # Explode the cursor and close the connection that are passed as arguments.
  close_cursor(cursor)
  close_connection(conn)
  print('Cursor and connection closed!')
