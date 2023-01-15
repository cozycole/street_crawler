import unittest
import os
import psycopg2 as pg
from dotenv import load_dotenv

from src import crawler as c

load_dotenv()

class TestCrawlerMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        user=os.getenv("POSTGRES_USER")
        password=os.getenv("POSTGRES_PASSWORD")
        host="localhost"
        db=os.getenv("POSTGRES_DB_NAME")
        pg_url = f"postgresql://{user}:{password}@{host}:5432/{db}"
        print(pg_url)
        cls.crawler = c.Crawler(
            db_str=pg_url,
            srid=3734,
            hood ="CUDELL",
            thread_count=1
        )

    def test_req_point_iteration(self):
        # We want to know:
        # 1. There exists a pano_id in pano_metadata
        # 2. There exists a point with a fk as that id
        # 3. The status of the point is "requested"
        conn = pg.connect(self.crawler.db_str)
        self.crawler.req_point_iteration(conn, None, None)
        conn.commit()

        curs = conn.cursor()

        curs.execute(
            """
            SELECT pano_id FROM pano_metadata LIMIT 1;
            """
        )
        pano_id = curs.fetchall()[0][0]
        print(pano_id)
        self.assertTrue(pano_id)

        curs.execute(
            f"""
            SELECT pano_id, status 
            FROM request_points
            WHERE pano_id = '{pano_id}'
            LIMIT 1;
            """
        )
        
        res = curs.fetchall()[0]
        print(res)
        self.assertEqual(res[0], pano_id)
        self.assertEqual(res[1], "requested")


