-- Create the database
CREATE DATABASE energy_saver;
USE energy_saver;
-- Create fresh users table
CREATE TABLE users (
    id int NOT NULL AUTO_INCREMENT,
    username varchar(100) NOT NULL,
    email varchar(100) NOT NULL,
    password varchar(255) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY (email)
);

