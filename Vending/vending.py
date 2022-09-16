import contextlib
import os
import sqlite3
from typing import Callable, Concatenate, Optional
import typing

import tabulate

schema = """
    CREATE TABLE IF NOT EXISTS products (
        id    TEXT    PRIMARY KEY,
        name  TEXT    NOT NULL,
        price INT
    );

    CREATE TABLE IF NOT EXISTS inventory (
        product_id  TEXT  PRIMARY KEY,
        count       INT   DEFAULT 5,

        FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
    );
"""


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def input_bool(question: str): 
    while True:
        resp = input(question).lower()
        if resp == "y":
            return True
        elif resp == "n":
            return False
        else:
            clear_screen()
            print("Invalid response, please type `Y` or `N`.")

def db_connect() -> sqlite3.Connection:
    connection = sqlite3.connect("vending.db")
    connection.executescript(schema)

    with contextlib.suppress(sqlite3.IntegrityError):
        connection.executescript("""
            INSERT INTO products(id, name, price)  VALUES('A1', 'Coca Cola', 100);
            INSERT INTO products(id, name, price) VALUES('A2', 'Lucazade (Original)', 150);
            INSERT INTO products(id, name, price) VALUES('A3', 'Lucazade (Orange)',   150);
            INSERT INTO products(id, name, price) VALUES('A4', 'Water',               75);
            INSERT INTO products(id, name, price) VALUES('A5', 'Orange Juice',        80);

            INSERT INTO inventory(product_id)         VALUES('A1');
            INSERT INTO inventory(product_id)         VALUES('A2');
            INSERT INTO inventory(product_id)         VALUES('A3');
            INSERT INTO inventory(product_id)         VALUES('A4');
            INSERT INTO inventory(product_id, count)  VALUES('A5', 0);
        """)

    return connection

P = typing.ParamSpec("P")
T = typing.TypeVar("T")

class VendingMachine:
    db_conn: sqlite3.Connection

    def __init__(self):
        self.db_conn = db_connect()

    def with_cursor(self, func: Callable[Concatenate[sqlite3.Cursor, P], T], *args: P.args, **kwargs: P.kwargs) -> T:
        cursor = self.db_conn.cursor()
        ret = func(cursor, *args, **kwargs)
        cursor.close()

        return ret


    def print_inventory(self, cursor: sqlite3.Cursor):
        cursor.execute("""
            SELECT inventory.product_id, products.name, inventory.count, products.price FROM inventory
            INNER JOIN products ON inventory.product_id=products.id
        """)

        data = cursor.fetchall()

        headers = ("Product ID", "Name", "Current Stock", "Price")
        tabluated = tabulate.tabulate(data, headers=headers).splitlines()
        
        # Cross out lines for products with no stock
        for (line, row) in enumerate(data):
            if row[2] == 0:
                STRIKE_THROUGH = "\u0336"
                tabluated[line + 2] = STRIKE_THROUGH.join(tabluated[line + 2])
        
        print("\n".join(tabluated))


    def select_product(self, cursor: sqlite3.Cursor) -> Optional[str]:
        product_id = input("Select a product: ")
        if product_id == "ResetDB":
            cursor.executescript("""
                DROP TABLE inventory;
                DROP TABLE products;
            """)

            return None

        cursor.execute("""
            SELECT name, price FROM products
            INNER JOIN inventory ON 
                products.id = inventory.product_id AND
                inventory.count > 1 

            WHERE id = ?;
        """, product_id)

        row: Optional[tuple[str, int]] = cursor.fetchone()
        if row is None:
            return None

        name, price = row
        price_pounds, price_pennies = divmod(price, 100)

        if input_bool(f"Are you sure you want to purchase `{name}` for £`{price_pounds}.{price_pennies}` (Y/N): "):
            return product_id

    def remove_stock(self, cursor: sqlite3.Cursor, product_id: str):
        cursor.execute("UPDATE ")


    def run(self):
        clear_screen()

        try:
            while True:
                self.with_cursor(self.print_inventory)

                product_id = self.with_cursor(self.select_product)
                if product_id is None:
                    clear_screen()
                    print("Product does not exist! Please enter a valid ID.")
                    continue

                self.with_cursor(self.remove_stock, product_id)
        finally:
            self.db_conn.close()    

while VendingMachine().run(): pass
