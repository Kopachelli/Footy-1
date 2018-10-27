try:
    import MySQLdb
except:
    import pymysql
    pymysql.install_as_MySQLdb()
    import MySQLdb
import mysql.connector
import os
import pandas as pd

def footy_connect(host=eval(os.environ['CONN_CRED'])['host'],
                  user=eval(os.environ['CONN_CRED'])['user'],
                  passwd=eval(os.environ['CONN_CRED'])['passwd'],
                  dbName=eval(os.environ['CONN_CRED'])['db']):

    footy_connect = MySQLdb.connect(
        host=host,
        user=user,
        passwd=passwd,
        db=dbName
    )
    print("Conection Made")
    return footy_connect

def create_tables(table_name):

    #connection to footy db in mysql
    conn = footy_connect()

    cursor = conn.cursor()

    query = """
        CREATE TABLE {0} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date VARCHAR(255) NOT NULL,
            home_team VARCHAR(255) NOT NULL,
            away_team VARCHAR(255) NOT NULL,
            home_team_goals INT NOT NULL,
            away_team_goals INT NOT NULL,
            full_time_results INT NOT NULL,
            ht_home_goals int NOT NULL,
            ht_away_goals int NOT NULL,
            ht_result VARCHAR(255) NOT NULL,
            home_team_shots INT DEFAULT NULL,
            away_team_shots INT DEFAULT NULL,
            home_team_shot_tar INT DEFAULT NULL,
            away_team_shot_tar INT DEFAULT NULL,
            home_corner INT DEFAULT NULL,
            away_corner INT DEFAULT NULL,
            home_foul INT DEFAULT NULL,
            away_foul INT DEFAULT NULL,
            home_yellow INT DEFAULT NULL, 
            away_yellow INT DEFAULT NULL,
            home_red INT DEFAULT NULL, 
            away_red INT DEFAULT NULL
        )   
    """
    cursor.execute(query.format(table_name))
    print("Table Created! " + str(table_name))

matches = create_tables("Scotland")
