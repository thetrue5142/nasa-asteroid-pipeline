CREATE TABLE IF NOT EXISTS asteroid_close_approaches (
    designation TEXT NOT NULL,
    julian_date_tdb TEXT NOT NULL,
    close_approach_tdb TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    distance_au DOUBLE PRECISION NOT NULL,
    velocity_km_s DOUBLE PRECISION NOT NULL,
    absolute_magnitude_h DOUBLE PRECISION,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (designation, julian_date_tdb),
    CONSTRAINT valid_distance CHECK (distance_au > 0),
    CONSTRAINT valid_velocity CHECK (velocity_km_s >= 0)
);
