import os
import sys
import tempfile
import unittest
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as application


class BusBookingTests(unittest.TestCase):

    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile(delete=False)
        self.db_file.close()
        application.DATABASE = self.db_file.name
        application.init_db()
        application.app.config["TESTING"] = True
        self.client = application.app.test_client()
        self.travel_date = (date.today() + timedelta(days=5)).isoformat()

    def tearDown(self):
        os.unlink(self.db_file.name)

    def booking(self, seat):
        return {"passenger": "Test User", "bus_id": 1,
                "seat_number": seat, "travel_date": self.travel_date}

    def test_health(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)

    def test_bus_search(self):
        r = self.client.get(
            f"/api/buses?source=Delhi&destination=Chandigarh&date={self.travel_date}")
        self.assertEqual(r.status_code, 200)
        self.assertGreater(len(r.json), 0)

    def test_booking(self):
        r = self.client.post("/api/bookings", json=self.booking(1))
        self.assertEqual(r.status_code, 201)

    def test_duplicate_seat(self):
        self.assertEqual(self.client.post("/api/bookings", json=self.booking(2)).status_code, 201)
        self.assertEqual(self.client.post("/api/bookings", json=self.booking(2)).status_code, 409)

    def test_cancel(self):
        r = self.client.post("/api/bookings", json=self.booking(3))
        bid = r.json["booking_id"]
        self.assertEqual(self.client.delete(f"/api/bookings/{bid}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/bookings/{bid}").status_code, 404)


if __name__ == "__main__":
    unittest.main()
