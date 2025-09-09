import sqlite3

conn = sqlite3.connect("amazon.db")
cur = conn.cursor()

cur.execute("Drop Table if exists products;")
cur.execute("Drop table if exists categories;")

cur.execute("""
create table categories(
    category_id integer primary key AUTOINCREMENT,
    category_name text unique
);
""")

cur.execute("""
create table products(
    product_id        integer primary key AUTOINCREMENT,
    product_name      text,
    category_id       integer,
    actual_price      REAL,
    discounted_price  REAL,
    discount_percent  REAL,
    rating            REAL,
    rating_count      INTEGER,
    foreign key(category_id) references categories(category_id)
);
""")


conn.commit()
conn.close()

print("Tables are created:)")
