import unittest
from dotenv import load_dotenv
import os
import requests
import psycopg2 as pg
import src.db_io as dbio
import src.google_io as glio

load_dotenv()

conn_str = os.getenv("DB_STRING")
api_key = os.getenv("G_API_KEY")

class TestGoogleUnDocAPI(unittest.TestCase):
    
    def test_from_file(self):
        with open("testing/found.txt","r") as f:
            meta_list = eval(f.read().replace(")]}\'\n", "").replace("null", "None"))
        
        self.assertEqual(meta_list[0][0][0], "Q76DoRlku6g8tN83aoLAZQ")
    
    def test_one_request(self):
        lat = 44.02265439596603 
        lon = -123.12405890734998
        correct_pano_id = "Q76DoRlku6g8tN83aoLAZQ"
        correct_pano_lat =  44.022688959104606
        correct_pano_lon = -123.1240688758301
        
        response = requests.get(f"https://www.google.com/maps/preview/photo?authuser=0&hl=en&gl=us&pb=!1e3!5m57!2m2!1i203!2i100!3m2!2i4!5b1!7m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!8m3!1m2!1e2!1e3!9b0!11m2!3b1!4b1!6m3!1sNTiiY6muJOjg0PEPi6CfsAg!7e81!15i11167!9m3!1d0!2d{lon}!3d{lat}!10d25")
        print(response.content.decode("utf-8"))

        decoded_response = eval(response.content.decode("utf-8").replace(")]}\'\n", "").replace("null", "None"))
        pano_id = decoded_response[0][0][0]
        lon, lat = decoded_response[0][0][8][0][1], decoded_response[0][0][8][0][2]
        
        self.assertEqual(lon, correct_pano_lon)
        self.assertEqual(lat, correct_pano_lat)
        self.assertEqual(pano_id, correct_pano_id)

    def test_undoc_loc_api(self):
        lat = 44.02265439596603 
        lon = -123.12405890734998
        correct_pano_id = "Q76DoRlku6g8tN83aoLAZQ"
        correct_pano_lat =  44.022688959104606
        correct_pano_lon = -123.1240688758301
        
        res_tup = glio.undoc_location_api_request(lat, lon)
        if not res_tup:
            raise Exception("res_tup is empty when it shouldn't be")

        (pano_id, res_lat, res_lon) = res_tup
        self.assertEqual(pano_id, correct_pano_id)
        self.assertEqual(res_lat, correct_pano_lat)
        self.assertEqual(res_lon, correct_pano_lon)
        
    def test_undoc_loc_api_null(self):
        # Alley way with no streetview imagery
        req_lat = 44.03289624812312
        req_lon = -123.068865444626
        self.assertEqual((), glio.undoc_location_api_request(req_lat, req_lon))