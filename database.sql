CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(100),
  email VARCHAR(100),
  password VARCHAR(256),
  created_at TIMESTAMP,
  PRIMARY KEY (id)
);