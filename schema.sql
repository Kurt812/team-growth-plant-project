DROP TABLE IF EXISTS gamma.recording;
DROP TABLE IF EXISTS gamma.plant;
DROP TABLE IF EXISTS gamma.botanist;

CREATE TABLE gamma.botanist(
    botanist_id INT IDENTITY(1,1) PRIMARY KEY,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(50) NOT NULL, 
    email VARCHAR(70) NOT NULL, 
    phone VARCHAR(20) NOT NULL 
);

CREATE TABLE gamma.plant(
    plant_id INT NOT NULL PRIMARY KEY, 
    botanist_id INT NOT NULL, 
    plant_name VARCHAR(100) NOT NULL, 
    FOREIGN KEY(botanist_id) REFERENCES gamma.botanist 
);

CREATE TABLE gamma.recording(
    recording_id INT IDENTITY(1,1) PRIMARY KEY, 
    plant_id INT NOT NULL,
    soil_moisture DECIMAL(8,2) NOT NULL,
    CONSTRAINT not_a_percentage CHECK(soil_moisture BETWEEN 0.00 AND 100.00), 
    temperature DECIMAL(8,2) NOT NULL,
    last_watered DATETIME, 
    recording_at DATETIME NOT NULL,
    FOREIGN KEY(plant_id) REFERENCES gamma.plant
);