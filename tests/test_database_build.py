import sqlite3

def test_db_exists():
    con=sqlite3.connect('db/analytics_casebook.sqlite')
    assert con.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='studies'").fetchone()[0]==1
    assert con.execute('PRAGMA foreign_key_check').fetchall()==[]
