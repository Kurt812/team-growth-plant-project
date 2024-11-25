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
    temperature DECIMAL(8,2) NOT NULL,
    last_watered TIMESTAMP NOT NULL, 
    recording_at TIMESTAMP NOT NULL,
    FOREIGN KEY(plant_id) REFERENCES plant
);