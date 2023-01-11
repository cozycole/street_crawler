-- Cole T. 1/11/23
-- These are functions that will be called by the crawler.
-- Initially, the function bodies were included in the Python code,
-- however, they are now organized into functions to be called by the Py process for readability.

CREATE OR REPLACE FUNCTION insert_pano_metadata(id varchar, lat numeric, lon numeric, date_str varchar, heading numeric)
    RETURNS void AS $$
        INSERT INTO pano_metadata (pano_id, capture_date, geom, heading)
        VALUES ((id, date_str, ST_SetSRID(ST_MakePoint(lon, lat), 4326), heading))
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION check_pano_id_exists(id varchar)
    RETURNS boolean AS $$
    SELECT EXISTS(SELECT 1 FROM pano_metadata WHERE pano_id = id);
$$ LANGUAGE SQL;

-- This function returns the gid passed to it, but has a side
-- effect of updating said gid to status 'progress'
CREATE OR REPLACE FUNCTION update_req_point_status(req_gid int, set_status varchar)
	RETURNS int AS $$
	BEGIN
		UPDATE request_points
		SET status = set_status
		WHERE request_points.gid = req_gid;
		
		RETURN req_gid;
	END;
$$ LANGUAGE plpgsql;

-- This function gets a random request point that is located within the hood if specified,
-- and atomically updates the row containing the gid's status to 'progress'. This means
-- multiple threads can call this function, and they will get a different gid to process. 
CREATE OR REPLACE FUNCTION get_random_request_point(hood_name varchar) 
        RETURNS TABLE (gid int, lat numeric, lon numeric) AS $$
		DECLARE
			req_gid int;
		BEGIN
			IF hood_name = '' THEN       
				WITH req_point AS (SELECT rp.gid
									FROM request_points as rp
									WHERE status is null OR status = '' 
									LIMIT 1
									FOR UPDATE)
				SELECT update_req_point_status(req_point.gid, 'progress') 
                FROM req_point INTO req_gid;
			ELSE
				WITH req_point AS (SELECT rp.gid
									FROM request_points as rp
									JOIN neighborhoods as n
									ON ST_Intersects(n.geom, rp.geom)
									WHERE n.hood_name = $1
									AND (status is null OR status = '') 
									LIMIT 1
									FOR UPDATE)
				SELECT update_req_point_status(req_point.gid, 'progress') 
                FROM req_point INTO req_gid;
			END IF;
			RETURN QUERY (
				SELECT rp.gid, ST_Y(rp.geom)::numeric as lat, ST_X(rp.geom)::numeric as lon
				FROM request_points as rp
				WHERE rp.gid = req_gid
			);
		END;
$$ LANGUAGE plpgsql; 
