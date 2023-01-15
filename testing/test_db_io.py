import os
import unittest
import psycopg2 as pg
from dotenv import load_dotenv
from src import db_io as dbio

load_dotenv()

class TestDBFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None: 
        # Set up database and tables
        cls.conn = pg.connect(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host="localhost",
            database=os.getenv("POSTGRES_DB_NAME")
        )

    def test_get_request_point(self):
        res = dbio.get_random_request_point(self.conn, "CUDELL")
        print(res)

        self.assertTrue(len(res) == 3)

    def test_get_request_point_null(self):
        res = dbio.get_random_request_point(self.conn, "NOT_A_HOOD")

        self.assertTrue(res == ())