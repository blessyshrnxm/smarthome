from flask_mysqldb import MySQL
from flask import current_app

mysql = MySQL()

def init_db(app):
    mysql.init_app(app)

def get_db():
    return mysql

def execute_query(query, params=None, fetch=True):
    """
    Execute a database query and optionally fetch results
    """
    cur = mysql.connection.cursor()
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        if fetch:
            result = cur.fetchall()
            return result
        else:
            mysql.connection.commit()
            return True
    except Exception as e:
        current_app.logger.error(f"Database error: {str(e)}")
        raise e
    finally:
        cur.close()

def insert_data(table, data):
    """
    Insert data into specified table
    """
    columns = ', '.join(data.keys())
    values = ', '.join(['%s'] * len(data))
    query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
    
    return execute_query(query, tuple(data.values()), fetch=False)

def get_user_by_email(email):
    """
    Get user by email
    """
    query = "SELECT * FROM users WHERE email = %s"
    result = execute_query(query, (email,))
    return result[0] if result else None

def get_user_stats(user_id):
    """
    Get user's energy usage statistics
    """
    query = """
        SELECT 
            AVG(usage_amount) as avg_usage,
            MIN(usage_amount) as min_usage,
            MAX(usage_amount) as max_usage,
            COUNT(*) as total_readings
        FROM energy_usage 
        WHERE user_id = %s
    """
    result = execute_query(query, (user_id,))
    return result[0] if result else None