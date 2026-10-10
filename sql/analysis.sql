SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT designation) AS distinct_objects,
    ROUND(MIN(distance_au)::numeric, 6) AS nearest_distance_au,
    ROUND(AVG(distance_au)::numeric, 6) AS average_distance_au,
    ROUND(MAX(velocity_km_s)::numeric, 2) AS maximum_velocity_km_s
FROM asteroid_close_approaches;

SELECT
    DATE_TRUNC('month', close_approach_tdb)::date AS approach_month,
    COUNT(*) AS approach_count,
    ROUND(AVG(distance_au)::numeric, 6) AS average_distance_au,
    ROUND(MIN(distance_au)::numeric, 6) AS nearest_distance_au
FROM asteroid_close_approaches
GROUP BY DATE_TRUNC('month', close_approach_tdb)
ORDER BY approach_month;

WITH converted_distances AS (
    SELECT
        designation,
        close_approach_tdb,
        distance_au,
        ROUND((distance_au * 149597870.7)::numeric, 0) AS distance_km,
        velocity_km_s
    FROM asteroid_close_approaches
)
SELECT
    designation,
    close_approach_tdb,
    ROUND(distance_au::numeric, 6) AS distance_au,
    distance_km,
    ROUND(velocity_km_s::numeric, 2) AS velocity_km_s
FROM converted_distances
ORDER BY distance_km, designation
LIMIT 10;

SELECT
    designation,
    close_approach_tdb,
    ROUND(distance_au::numeric, 6) AS distance_au,
    ROW_NUMBER() OVER (
        ORDER BY distance_au, designation, julian_date_tdb
    ) AS overall_distance_rank,
    ROW_NUMBER() OVER (
        PARTITION BY DATE_TRUNC('month', close_approach_tdb)
        ORDER BY distance_au, designation, julian_date_tdb
    ) AS monthly_distance_rank,
    ROUND(AVG(distance_au) OVER ()::numeric, 6) AS overall_average_distance_au
FROM asteroid_close_approaches
ORDER BY overall_distance_rank
LIMIT 20;
