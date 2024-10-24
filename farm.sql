CREATE DATABASE idolday CHARACTER SET utf8mb4;

CREATE TABLE xox (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    group_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) AUTO_INCREMENT=1000;

CREATE TABLE xox_group (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    management_company_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) AUTO_INCREMENT=1000;

CREATE TABLE management_company (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) AUTO_INCREMENT=1000;


-- CREATE TABLE users (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     phone_number VARCHAR(255) NOT NULL DEFAULT '',
--     email VARCHAR(255) NOT NULL DEFAULT '',
--     username VARCHAR(255) NOT NULL,
--     password_hash VARCHAR(255) NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     avatar_name VARCHAR(255) NOT NULL DEFAULT 'persimmon'  -- 之后存在 key:value 数据库中
-- ) AUTO_INCREMENT=1000;

-- CREATE TABLE devices (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     type INT NOT NULL,             -- 设备类型，如移动音响
--     device_id VARCHAR(255) NOT NULL UNIQUE,
--     user_id INT NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- ) AUTO_INCREMENT=1000;

-- CREATE TABLE device_tokens (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     device_id VARCHAR(255) NOT NULL,
--     token VARCHAR(255) NOT NULL,
--     expired_at TIMESTAMP NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- ) AUTO_INCREMENT=1000;

------ admin ------
-- CREATE TABLE admin_users (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     username VARCHAR(255) NOT NULL,
--     password_hash VARCHAR(255) NOT NULL,
--     display_name VARCHAR(255) NOT NULL
-- ) AUTO_INCREMENT=1000;

-- CREATE TABLE switches (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     switch_key VARCHAR(255) NOT NULL,
--     switch_value INT NOT NULL
-- ) AUTO_INCREMENT=1000;


