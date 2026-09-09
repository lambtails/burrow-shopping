from flask import Flask, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix
import sqlite3
import datetime
import csv

# Create database connection
db = "database.db"
detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES

# Create database table if it doesn't exist
with sqlite3.connect(db, detect_types=detect_types) as connect:
    connect.execute("""
        CREATE TABLE IF NOT EXISTS ShoppingList (
        RowID INTEGER NOT NULL PRIMARY KEY,
        Item TEXT NOT NULL,
        Category TEXT,
        LastUpdated TIMESTAMP,
        Done BOOL NOT NULL,
        UNIQUE(Item)
        );
        """)

# Load groceries into database if they're not already in it
with open("groceries.csv", "r") as csv_file:
    # Load csv file and skip header
    grocery_reader = csv.reader(csv_file, delimiter=",", quotechar='"')
    next(grocery_reader, None)

    # Connect to database and add groceries
    with sqlite3.connect(db, detect_types=detect_types) as connect:
        cursor = connect.cursor()
        for row in grocery_reader:
            cursor.execute(
                """
                INSERT OR IGNORE INTO ShoppingList (Item, Category, Done, LastUpdated) 
                VALUES (?,?,?,?);
                """,
                (row[0], row[1], True, datetime.datetime.now()),
            )
        connect.commit()
        cursor.close()


# Start flask app and define URL routes
app = Flask(__name__, static_folder="static")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)


@app.route("/", methods=["GET"])
def index():
    # Connect and load database for GET request
    with sqlite3.connect(db, detect_types=detect_types) as connect:
        cursor = connect.cursor()
        cursor.execute(
            """
            SELECT *
            FROM ShoppingList
            ORDER BY Done ASC, Category ASC, LastUpdated ASC;
            """,
        )
        data = cursor.fetchall()
        cursor.close()

    # Render webpage
    return render_template(
        "index.html",
        data=data,
    )


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
            UPDATE ShoppingList
            SET Done=?, LastUpdated=?
            WHERE RowID=?;
            """,
            (done, datetime.datetime.now(), row_id),
        )
        connect.commit()
        cursor.close()

    # Return empty string
    return ""


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
