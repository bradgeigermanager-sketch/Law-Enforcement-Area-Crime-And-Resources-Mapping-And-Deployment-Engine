SELECT i.incident_id, s.title, ST_Distance(i.geom_location, f.geom_location, true) as distance_meters
FROM crime_incidents i
JOIN statutory_codes s ON i.statute_id = s.statute_id
JOIN judicial_facilities f ON f.name = 'Central District Courthouse'
WHERE ST_DWithin(i.geom_location, f.geom_location, 500, true); -- "true" uses geodesic distance in meters

