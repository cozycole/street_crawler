"""
This file contains functions that handle all
API requests to Google for the crawler object. 
"""
import requests
import logging
log = logging.getLogger('crawler')

from src import io_data as iod

def find_pano(lat: float, lon: float, retry = 3, headers: dict = None, proxy: str = None): 
    """Sends api call for pano metadata located near (lat, lon)
    Args:
        lat (float): lat val
        lon (float): lon val
        api_key (optional, str): Google api key

    Returns:
        dict: result containing pano metadata
    """
    for i in range(1,retry+1):    
        try:
            return undoc_location_api_request(lat, lon, headers, proxy)   
        except requests.exceptions.HTTPError:
            log.exception(f"undoc_location_api: http error for request at ({lat},{lon})")
            raise requests.exceptions.HTTPError
        except requests.exceptions.Timeout:
            log.error(f"undoc_location_api: timeout error for request at ({lat},{lon})")
            if i > 2:
                raise Exception("Retry count exceeded")

def undoc_location_api_request(lat, lon, headers=None, proxy=None) -> 'tuple(str, float, float)':
    try:    
        url = iod.UNDOC_LOCATION_API % (lon, lat)
        response = requests.get(url, headers=headers, proxies=proxy)
        response.raise_for_status()
        
        decoded_response = decode_response(response) 
        print(decoded_response)
        
        pano_id = get_id_from_decoded_response(decoded_response)
        pano_lon, pano_lat = get_latlon_from_decoded_response(decoded_response)
        return (pano_id, pano_lat, pano_lon)
    except TypeError:
        # catches responses that do not have a closest pano
        # which will not have the correct value types leading
        # to to attempting subscript of a None value 
        log.debug(f"No pano near ({lat},{lon})")
        return ()
        
def decode_response(response: 'requests.Response') -> list:
    decoded_response = response.content \
                    .decode("utf-8") \
                    .replace(")]}\'\n", "") \
                    .replace("null", "None")  
    return eval(decoded_response)

def get_id_from_decoded_response(response: 'requests.Response'):
    pano_id = response[0][0][0]
    return pano_id

def get_latlon_from_decoded_response(response: 'requests.Response'):
    lon, lat = response[0][0][8][0][1], response[0][0][8][0][2]
    return lon, lat

# def official_api_request(lat, lon, api_key):
#     url = iod.DOC_API % (lat, lon, api_key)
#     res = requests.get(url)
#     return res.json()