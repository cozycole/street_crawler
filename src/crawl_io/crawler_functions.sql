-- Cole T. 1/11/23
-- These are functions that will be called by the crawler.
-- Initially, the function bodies were included in the Python code,
-- however, they are now organized into functions to be called by the Py process for readability.

CREATE OR REPLACE FUNCTION insert_pano_metadata(id varchar, lat numeric, lon numeric)
    RETURNS void AS $$
        INSERT INTO pano_metadata (pano_id, geom)
        VALUES (id, ST_SetSRID(ST_MakePoint(lon, lat), 4326))
        ON CONFLICT DO NOTHING
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION set_req_point_pano_fk(req_gid int, pano_id_fk varchar)
    RETURNS void AS $$
    UPDATE request_points
    SET pano_id = pano_id_fk
    WHERE gid = req_gid;
$$ LANGUAGE SQL;

-- This function returns the gid passed to it, but has a side
-- effect of updating said gid to status set_status 
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

-- NOTE: Setting the status to 'progress' is not necessarily needed, since the row lock
-- on the given req_point carries over throughout an entire transaction. So if I had desiged
-- the application to do an entire req_point iteration (get req_point, send api req, update table)
-- in a single transaction, the row would remain locked, and updating the status would be unecessary. 
-- (this is in hindsight)
CREATE OR REPLACE FUNCTION get_random_request_point(hood_name varchar) 
        RETURNS TABLE (gid int, lat double precision, lon double precision) AS $$
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
			RETURN QUERY 
				SELECT rp.gid, ST_Y(rp.geom)::double precision as lat, ST_X(rp.geom)::double precision as lon
				FROM request_points as rp
				WHERE rp.gid = req_gid;
		END;
$$ LANGUAGE plpgsql; 
