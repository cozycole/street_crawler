"""
Goals:
- Interact with database to make api requests for (lat, lon) points
along street linestring geometries stored in a database table {city}_streets.
- Handle the result, and store valid results to pano_metadata
"""
import logging
import logging.config
import logging.handlers

log = logging.getLogger("crawler")

import threading
import copy
import psycopg2 as pg
from time import sleep
import random

import src.crawl_io.db_io as dbio
import src.crawl_io.google_io as glio

class Crawler():

    def __init__(
        self, 
        db_str, 
        srid, 
        hood = "", 
        thread_count = 1, 
        retry = 3, 
        proxies = None,
        proxy_url = None,
        header = None,
        agents = None):
        """
        Crawler used to increment along GIS street segments and make API
        request to find panos.

        Args:
            db_str (str): postgres url
            srid (int): local srid for GIS distance calculations
            hood (str, optional): neighborhood to crawl
            retry (int), optional): # of times to retry request
        """ 
        self.db_str = db_str
        self.hood = hood
        self.srid = srid
        self.retry = retry
        self.proxies = proxies
        self.header = header
        self.agents = agents
        self.thread_count = thread_count
        self.proxy_template = proxy_url
        
        if hood:
            log.debug(f"Crawler initialized with location:{hood}")
    
    def start_crawl(self):
        kill_event = threading.Event()
        self._start_crawl_monitor(kill_event, self.thread_count)

    def _start_crawl_monitor(self,  kill_event: threading.Event, thread_count):
        """
        Spawns crawler threads and checks the multiprocessing.Event
        for a kill switch to join the threads.

        Args:
            e (multiprocessing.Event): communication with main thread
            thread_count (int): # of threads to spawn
        """
        log.debug("starting crawler monitor...")

        threads = []
        thread_count = thread_count if 3 >= thread_count > 0 else 1
        
        for i in range(thread_count):
            th = threading.Thread(target=self._start_crawl_loop,
                                args=(kill_event, i))
            th.start()
            threads.append(th)
            sleep(10)
        try:
            while True:
                sleep(5)
        except KeyboardInterrupt:
            log.debug("Interupt detected from crawl_monitor")
            kill_event.set()
            for thread in threads:
                thread.join()
            log.debug("Exiting crawler monitor process")

    def _start_crawl_loop(self, kill_event: threading.Event, thread_id, err_thres = 3):
        """Note we do not have to worry about half baked req point processing when errors occur since
        they all occur in a transaction which is committed in its entirety or rolledback on error.

        Args:
            conn (pg.connection): pg conn
            e (threading.Event): event to check for thread termination
            thread_id (int): for logging
            err_thres (int, optional): # of errors before terminating thread. Defaults to 3.
        """
        # create copy of header for this thread since each thread will inserting a user agent
        thread_header = copy.copy(self.header)
        conn = pg.connect(self.db_str)
        err_count = 0
        while True:
            header = glio.generate_header(thread_header, self.agents, thread_id) 
            proxy = glio.choose_proxy(self.proxy_template, self.proxies, thread_id)
            # glio.test_proxy(proxy)
            glio.test_header(header)
            input("continue")
            try:
                if kill_event.is_set():
                    log.debug(f"Thread {thread_id}: termination flag set, exiting thread")
                    conn.close()
                    break

                if self.req_point_iteration(conn, header, proxy):
                    log.debug(f"Thread {thread_id}: No more points to request! Terminating thread...")
                    break
                conn.commit()
                err_count = 0
                sleep(random.randint(15,20))
            except Exception as e:
                log.exception(e)
                err_count += 1
                conn.rollback()
                if err_count >= err_thres:
                    log.critical(f"Thread {thread_id}: error count exceeded, terminating thread")
                    break
                sleep(random.randint(15,20))
                    
    def req_point_iteration(self, conn: 'pg.connection', header, proxy) -> bool:
        """Handles all operations needed for requesting and processing a single req point.
        This function is to be called in a loop

        Args:
            conn : pg conn
            header : a header dictionary to be used for api req  
            proxy : a proxy ip address to be used for api req

        Returns:
            bool : finished status (when no more points are left to request) 
        """
        req_point = dbio.get_random_request_point(conn, self.hood)
        
        if not req_point:
            return True

        gid, lat, lon = req_point
        log.debug(f"Requesting point with gid {gid} @ ({lat}, {lon})")
        pano_data = glio.find_pano(
            lat = lat,
            lon = lon,
            headers = header,
            proxy = proxy,
            retry = self.retry
        )

        if pano_data:
            pano_id, lat, lon = pano_data
            log.debug(f"Pano with id {pano_id} found near req_point gid {gid}")
            dbio.insert_pano_data(conn, pano_id, lat, lon)
            dbio.set_req_point_fk(conn, gid, pano_id)
        dbio.update_req_point_status(conn, gid, "requested")
        return False
    