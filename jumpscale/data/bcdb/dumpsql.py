def main():
    import sqlite3
    from pprint import pprint

    conn = sqlite3.connect("test_index.db")
    c = conn.cursor()
    c.execute("SELECT * FROM employee_name")
    pprint(c.fetchall())
    c.execute("SELECT * FROM employee_salary")
    pprint(c.fetchall())


if __name__ == "__main__":
    main()
