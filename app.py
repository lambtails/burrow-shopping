from flask import Flask, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix
import sqlite3
import datetime
import csv
import re

# Create database connection
db = "database.db"
detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES


def setup_database():
    # Create database table if it doesn't exist
    with sqlite3.connect(db, detect_types=detect_types) as connect:
        connect.execute("""
            CREATE TABLE IF NOT EXISTS groceries (
                groceryname TEXT NOT NULL PRIMARY KEY,
                category TEXT,
                icon TEXT,
                tags TEXT,
                aldi BOOL,
                coles BOOL
            );
            """)
        connect.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                category TEXT NOT NULL PRIMARY KEY,
                colour TEXT,
                modifier TEXT
            );
            """)
        connect.execute("""
            CREATE TABLE IF NOT EXISTS shoppinglist (
                rowid INTEGER NOT NULL PRIMARY KEY,
                listgrocery TEXT NOT NULL,
                lastupdated TIMESTAMP,
                done BOOL NOT NULL,
                FOREIGN KEY(listgrocery) REFERENCES groceries(groceryname),
                UNIQUE(listgrocery)
            );
            """)

    # Load categories into database if they're not already in it
    with open("categories.csv", "r") as csv_file:
        # Load csv
        category_reader = csv.reader(csv_file, delimiter=",", quotechar='"')
        next(category_reader, None)

        # Connect to database and add categories
        with sqlite3.connect(db, detect_types=detect_types) as connect:
            cursor = connect.cursor()
            for row in category_reader:
                # Get CSV data
                category = row[0].upper()
                colour = row[1]
                modifier = row[2]

                # Add new rows for categories
                cursor.execute(
                    """
                        INSERT OR IGNORE INTO categories (category, colour, modifier) 
                        VALUES (?,?,?);
                        """,
                    (category, colour, modifier),
                )

                # Update all existing categories with any new data
                cursor.execute(
                    """
                    UPDATE categories
                    SET colour=?, modifier=?
                    WHERE category=?;
                    """,
                    (colour, modifier, category),
                )

    # Load groceries into database if they're not already in it
    with open("groceries.csv", "r") as csv_file:
        # Load csv file and skip header
        grocery_reader = csv.reader(csv_file, delimiter=",", quotechar='"')
        next(grocery_reader, None)

        # Connect to database and add groceries
        with sqlite3.connect(db, detect_types=detect_types) as connect:
            cursor = connect.cursor()
            for row in grocery_reader:
                # Get CSV data
                name = row[0].upper()
                category = row[1].upper()
                icon = row[2]
                aldi = row[3]
                coles = row[4]
                tags = row[5].upper()

                # Add new rows for groceries
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO groceries (groceryname, category, icon, aldi, coles, tags) 
                    VALUES (?,?,?,?,?,?);
                    """,
                    (name, category, icon, aldi, coles, tags),
                )

                # Update all existing groceries with any new data
                cursor.execute(
                    """
                    UPDATE groceries
                    SET category=?, icon=?, aldi=?, coles=?, tags=?
                    WHERE groceryname=?;
                    """,
                    (category, icon, aldi, coles, tags, name),
                )

                # Also add new groceries into the shopping list (so they can be shopped)
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO shoppinglist (listgrocery, lastupdated, done) 
                    VALUES (?,?,?);
                    """,
                    (name, datetime.datetime.now(), True),
                )
            connect.commit()
            cursor.close()


# Start flask app and define URL routes
app = Flask(__name__, static_folder="static")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
setup_database()


@app.route("/", methods=["GET"])
def index():
    # Connect and load database for GET request
    with sqlite3.connect(db, detect_types=detect_types) as connect:
        cursor = connect.cursor()
        cursor.execute(
            """
            SELECT rowid, groceryname, groceries.category AS category, icon, colour, aldi, coles, tags, lastupdated, done, modifier
            FROM shoppinglist
            INNER JOIN groceries ON shoppinglist.listgrocery = groceries.groceryname
            INNER JOIN categories ON groceries.category = categories.category
            ORDER BY done ASC, groceries.category ASC, lastupdated ASC;
            """,
        )
        names = list(map(lambda x: x[0], cursor.description))
        data = [dict(zip(names, row)) for row in cursor.fetchall()]
        defaults = {"icon": "pixel.png", "aldi": "true", "coles": "true"}
        for i in range(len(data)):
            row = data[i]
            for k, v in defaults.items():
                if row[k] == "":
                    row[k] = v
            data[i] = row
        cursor.close()

    # Render webpage
    return render_template("index.html", data=data)


@app.route("/update", methods=["POST"])
def update():
    # Get data from the JSON request
    row_id: int = int(request.json.get("row_id"))
    done: bool | None = request.json.get("done")

    # Update the database
    with sqlite3.connect(db, detect_types=detect_types) as connect:
        cursor = connect.cursor()
        cursor.execute(
            """
            UPDATE shoppinglist
            SET done=?, lastupdated=?
            WHERE rowid=?;
            """,
            (done, datetime.datetime.now(), row_id),
        )
        connect.commit()
        cursor.close()

    # Return empty string
    return ""


@app.route("/new-item", methods=["POST"])
def new_item():
    # Get data from the JSON request
    name: str = request.json.get("name")

    # Validate/sanitize the input name
    name = re.sub(r"[^A-Za-z\d\s,.-]+", "", name)
    name = name.strip().upper()
    if len(name) == 0:
        return ""

    # Add the new item to the shopping list with default parameters
    with sqlite3.connect(db, detect_types=detect_types) as connect:
        cursor = connect.cursor()

        # Add to groceries database
        cursor.execute(
            """
            INSERT OR IGNORE INTO groceries (groceryname, category, icon, aldi, coles, tags) 
            VALUES (?,?,?,?,?,?);
            """,
            (name, "DEFAULT", "", True, True, ""),
        )

        # Add to shopping list
        cursor.execute(
            """
            INSERT OR IGNORE INTO shoppinglist (listgrocery, lastupdated, done) 
            VALUES (?,?,?);
            """,
            (name, datetime.datetime.now(), False),
        )

        # Set done to False since we assume the user wants to mark new items for shopping
        # This also means if the user enters an item already in the list, it will still update something
        # Rather than appearing to fail silently
        cursor.execute(
            """
            UPDATE shoppinglist
            SET done=?, lastupdated=?
            WHERE listgrocery=?;
            """,
            (False, datetime.datetime.now(), name),
        )

        connect.commit()
        cursor.close()

    # Refresh the page
    return app.redirect(app.url_for(endpoint="index"))


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
