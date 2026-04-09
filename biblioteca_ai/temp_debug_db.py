import pyodbc
from db import SERVER, DATABASE, CREDENTIALS

print('SERVER:', SERVER)
print('DATABASE:', DATABASE)

for role, creds in CREDENTIALS.items():
    try:
        conn_str = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={SERVER};'
            f'DATABASE={DATABASE};'
            f'UID={creds["username"]};'
            f'PWD={creds["password"]};'
            'TrustServerCertificate=yes;'
        )
        print('Trying', role, conn_str)
        cn = pyodbc.connect(conn_str, timeout=5)
        cur = cn.cursor()
        cur.execute('SELECT TOP 1 * FROM dbo.Users')
        rows = cur.fetchall()
        print(role, 'OK', len(rows), rows[:1])
        cn.close()
    except Exception as e:
        print(role, 'ERROR', e)
