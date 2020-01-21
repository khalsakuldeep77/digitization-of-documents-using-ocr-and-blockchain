import sqlite3
def query_designation(designation):
    conn=sqlite3.connect('registration.db')
    c=conn.cursor()
    statement='SELECT * FROM users WHERE designation = "{}"'.format(designation)
    print(statement)
    c.execute(statement)
    data=c.fetchall()
    for row in data:
        print(row)
    c.close()
    conn.close()
query_designation('Actor')
