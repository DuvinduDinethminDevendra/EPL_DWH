import mysql.connector

cfg = {'host':'127.0.0.1','user':'root','password':'1234','database':'epl_dw','port':3307}
conn = mysql.connector.connect(**cfg)
c = conn.cursor()

queries = [
    ("SELECT COUNT(*) FROM dim_player", 'dim_player rows'),
    ("SELECT COUNT(*) FROM dim_team", 'dim_team rows'),
    ("SELECT COUNT(*) FROM fact_match", 'fact_match rows'),
    ("SELECT COUNT(*) FROM fact_player_stats", 'fact_player_stats rows'),
    ("SELECT COUNT(*) FROM fact_match_events", 'fact_match_events rows'),
    ("SELECT player_id, player_name FROM dim_player WHERE player_id IN (-1,6808)", 'sentinel players'),
]

for sql, label in queries:
    try:
        c.execute(sql)
        rows = c.fetchall()
        print(label + ':', rows)
    except Exception as e:
        print('ERROR running', label, e)

c.close()
conn.close()
