"""
This module handles all database I/O functions.
It simply calls the stored SQL functions found in crawler_functions.sql.
"""
import psycopg2 as pg
import logging
log = logging.getLogger('crawler')

def get_random_request_point(conn: 'pg.connection', hood_name = ""):
    curs = conn.cursor()
    # Future ref: the ().* is needed for notifying pg to treat 
    # the column fields individually. Before it was a string of a tuple (i.e. '(1,2,3)')
    # but this allows it to resolve the individual element types.
    query = f"SELECT (get_random_request_point('{hood_name}')).*;"
    curs.execute(query)
    res = curs.fetchall()
    curs.close()
    if res:
        return res[0]
    return ()

def insert_pano_data(conn: 'pg.connection', pano_id, lat, lon):
    curs = conn.cursor()
    query = f"SELECT insert_pano_metadata('{pano_id}', {lat}, {lon});"
    curs.execute(query)
    curs.close()
    
def set_req_point_fk(conn: 'pg.connection', gid: int, pano_id: str):
    curs = conn.cursor()
    query = f"SELECT set_req_point_pano_fk({gid}, '{pano_id}');"
    curs.execute(query)
    curs.close()

def update_req_point_status(conn: 'pg.connection', gid: int, status: str):
    curs = conn.cursor()
    query = f"SELECT update_req_point_status({gid}, '{status}');"
    curs.execute(query)
    curs.close()
