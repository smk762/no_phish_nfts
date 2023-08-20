#!/usr/bin/env python3
from db.sessions import create_tables

q = input("This will drop any existing tables and data, then create new, empty tables. Confirm? [Y/y]")
if q.lower() == "y":
    create_tables()
    print("Tables created.")
else:
    print("Tables not created.")

