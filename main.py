import os
import logging.config
from log_config import LOGGING_CONFIG
from src import crawler as craw
from src import io_data as iod
from dotenv import load_dotenv

logging.config.dictConfig(LOGGING_CONFIG)
load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
db_name = os.getenv("POSTGRES_DB_NAME")
DB_CONN_STR = f"postgresql://{user}:{password}@{host}:5432/{db_name}"

def get_proxies(file_str) -> list:
    proxy_list = []
    if os.path.exists(file_str):
        with open(file_str, "r") as fp:
            for line in fp:
               proxy_list.append(line.strip().replace("\n", "").split(",")[0]) 
    return proxy_list

def main():
    env_thread_cnt = int(os.getenv("THREAD_COUNT"))
    thread_count =  env_thread_cnt if env_thread_cnt else 1
    proxies = get_proxies("proxies.txt")
    print(proxies)
    crawler = craw.Crawler(
        db_str=DB_CONN_STR,
        srid=os.getenv("SRID"),
        hood="EDGEWATER",
        thread_count=thread_count,
        proxies=proxies,
        proxy_url=os.getenv("PROXY_URL"),
        header=iod.HEADER_TEMPLATE,
        agents=iod.AGENTS
    )
    crawler.start_crawl()

if __name__ == "__main__":
    main()