#!/bin/bash
sqlite3 db.sqlite3 -cmd ".mode csv" ".import data.csv recommender_musicdata" "delete from recommender_musicdata where valence='valence'"
