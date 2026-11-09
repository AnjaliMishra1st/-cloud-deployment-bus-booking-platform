import os
import sqlite3
from datetime import date
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

DATABASE = os.environ.get("DATABASE_PATH", "bus_booking.db")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source TEXT NOT NULL,
            destination TEXT NOT NULL,
            departure TEXT NOT NULL,
            arrival TEXT NOT NULL,
            price REAL NOT NULL,
            total_seats INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passenger TEXT NOT NULL,
            bus_id INTEGER NOT NULL,
            seat_number INTEGER NOT NULL,
            travel_date TEXT NOT NULL,
            FOREIGN KEY(bus_id) REFERENCES buses(id),
            UNIQUE(bus_id, seat_number, travel_date)
        )
    """)
    count = conn.execute("SELECT COUNT(*) FROM buses").fetchone()[0]
    if count == 0:
        buses = [
            ("Volvo Express", "Delhi", "Chandigarh", "08:00 AM", "12:00 PM", 650, 40),
            ("City Travels", "Delhi", "Chandigarh", "10:00 AM", "02:00 PM", 500, 40),
            ("Green Line", "Delhi", "Chandigarh", "06:00 PM", "10:00 PM", 450, 40),
            ("Royal Travels", "Chandigarh", "Delhi", "09:00 AM", "01:00 PM", 550, 40),
            ("Night Rider", "Delhi", "Jaipur", "10:00 PM", "05:00 AM", 800, 40),
            ("Punjab Express", "Ludhiana", "Delhi", "07:00 AM", "01:00 PM", 600, 40),
            ("Doaba Travels", "Nawanshahr", "Chandigarh", "07:30 AM", "11:00 AM", 300, 40),
            ("Doaba Travels", "Chandigarh", "Nawanshahr", "04:00 PM", "07:30 PM", 300, 40),
            ("Jalandhar Link", "Jalandhar", "Delhi", "06:00 AM", "01:00 PM", 700, 40),
            ("Jalandhar Link", "Delhi", "Jalandhar", "03:00 PM", "10:00 PM", 700, 40),
            ("Golden Temple Express", "Amritsar", "Delhi", "08:30 PM", "05:30 AM", 850, 40),
            ("Golden Temple Express", "Delhi", "Amritsar", "09:00 PM", "06:00 AM", 850, 40),
            ("Nawanshahr Express", "Nawanshahr", "Jalandhar", "09:00 AM", "10:30 AM", 120, 40),
            ("Nawanshahr Express", "Jalandhar", "Nawanshahr", "05:00 PM", "06:30 PM", 120, 40),
            ("Punjab Roadways", "Ludhiana", "Chandigarh", "11:00 AM", "01:30 PM", 250, 40),
        ]
        conn.executemany("""
            INSERT INTO buses
            (name, source, destination, departure, arrival, price, total_seats)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, buses)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "healthy", "application": "Bus Booking Platform"})


@app.route("/api/buses")
def get_buses():
    source = request.args.get("source", "").strip()
    destination = request.args.get("destination", "").strip()
    travel_date = request.args.get("date", "").strip()
    conn = get_db()
    buses = conn.execute("""
        SELECT b.*,
        b.total_seats - (
            SELECT COUNT(*) FROM bookings bk
            WHERE bk.bus_id = b.id AND bk.travel_date = ?
        ) AS available_seats
        FROM buses b
        WHERE LOWER(b.source) LIKE LOWER(?)
        AND LOWER(b.destination) LIKE LOWER(?)
        ORDER BY b.id
    """, (travel_date, f"%{source}%", f"%{destination}%")).fetchall()
    conn.close()
    return jsonify([dict(bus) for bus in buses])


@app.route("/api/bookings", methods=["POST"])
def create_booking():
    data = request.get_json(silent=True) or {}
    passenger = str(data.get("passenger", "")).strip()
    travel_date = str(data.get("travel_date", "")).strip()
    try:
        bus_id = int(data.get("bus_id"))
        seat_number = int(data.get("seat_number"))
        parsed_date = date.fromisoformat(travel_date)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid booking details"}), 400

    if not passenger or len(passenger) > 100:
        return jsonify({"error": "Enter a valid passenger name"}), 400
    if parsed_date < date.today():
        return jsonify({"error": "Travel date cannot be in the past"}), 400

    conn = get_db()
    try:
        bus = conn.execute("SELECT * FROM buses WHERE id = ?", (bus_id,)).fetchone()
        if not bus:
            return jsonify({"error": "Bus not found"}), 404
        if seat_number < 1 or seat_number > bus["total_seats"]:
            return jsonify({"error": "Invalid seat number"}), 400
        cursor = conn.execute("""
            INSERT INTO bookings (passenger, bus_id, seat_number, travel_date)
            VALUES (?, ?, ?, ?)
        """, (passenger, bus_id, seat_number, travel_date))
        conn.commit()
        return jsonify({
            "message": "Booking successful",
            "booking_id": cursor.lastrowid,
            "passenger": passenger,
            "seat_number": seat_number
        }), 201
    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({"error": "This seat is already booked"}), 409
    finally:
        conn.close()


@app.route("/api/bookings")
def get_bookings():
    conn = get_db()
    rows = conn.execute("""
        SELECT bk.id, bk.passenger, bk.seat_number, bk.travel_date,
        b.name AS bus_name, b.source, b.destination, b.price
        FROM bookings bk JOIN buses b ON bk.bus_id = b.id
        ORDER BY bk.id DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
def cancel_booking(booking_id):
    conn = get_db()
    cursor = conn.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        return jsonify({"error": "Booking not found"}), 404
    return jsonify({"message": "Booking cancelled successfully"})


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
