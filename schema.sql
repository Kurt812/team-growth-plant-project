DROP TABLE IF EXISTS recording;
DROP TABLE IF EXISTS plant;
DROP TABLE IF EXISTS botanist;

CREATE TABLE botanist(
    botanist_id INT NOT NULL PRIMARY KEY,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(50) NOT NULL, 
    email VARCHAR(70) NOT NULL, 
    phone VARCHAR(15) NOT NULL 
);

CREATE TABLE plant(
    plant_id INT NOT NULL PRIMARY KEY, 
    botanist_id INT NOT NULL, 
    plant_name VARCHAR(100) NOT NULL, 
    FOREIGN KEY(botanist_id) REFERENCES botanist 
);

CREATE TABLE recording(
    recording_id INT NOT NULL PRIMARY KEY, 
    plant_id INT NOT NULL,
    soil_moisture DECIMAL(8,2) NOT NULL,
    CONSTRAINT not_a_percentage CHECK(soil_moisture BETWEEN 0.00 AND 100.00), 
    temperature DECIMAL(8,2) NOT NULL,
    CONSTRAINT not_valid_temperature CHECK(temperature BETWEEN -10.00 AND 25),
    last_watered DATETIME, 
    recording_at DATETIME NOT NULL,
    FOREIGN KEY(plant_id) REFERENCES plant
);