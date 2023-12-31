# FutBin Database For EA FC24
Web-scraping script, writes the data of all the players from FutBin to a CSV file and MySQL Database

What is the purpose of this script?

The purpose of this repository is to have a script that automatically pulls down all players data from FUTBIN website for the videogame EA FC 24 and allows to have a new updated database.

How to use it?

Just run the futbin.py:

Doing "python futbin.py" to get Futbin data.

Players data ouput format:

After running the script the user will have the data saved in a CSV file and in a MySQL Database file.

Requirements:

Python 3

PIP

MySQLdb

You will need to use PIP to install the following libraries:

bs4

requests

pandas

MySQLdb


********** You need to create a table to store as a Database for MySQL, I did it for you too: **********

CREATE TABLE IF NOT EXISTS EAFC24 (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255),
    Rating INT,
    Price VARCHAR(255),
    PercentageChange VARCHAR(255),
    SkillsMoves INT,
    WeakFoot INT,
    Pace INT,
    Shooting INT,
    Passing INT,
    Dribbling INT,
    Defending INT,
    Physicality INT,
    Height VARCHAR(255),
    Division VARCHAR(255),
    Inches VARCHAR(255),
    Popularity VARCHAR(255),
    BaseStats VARCHAR(255),
    IngameStats VARCHAR(255),
    Nothing VARCHAR(255),
    Position VARCHAR(255),
    Club VARCHAR(255),
    Country VARCHAR(255),
    League VARCHAR(255),
    NationPic VARCHAR(255),
    ClubPic VARCHAR(255),
    PlayerPic VARCHAR(255),
    LOADDATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


To create/use the table do this in your MySQL 8.0 Command Line Client: 

USE FUTBIN;
then copy/paste my table
DESCRIBE EAFC24; (to check if it's properly created)

That's it now you can manage and choose what you need.
