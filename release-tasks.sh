#!/bin/sh

if [[ ! -f "information.db" ]]
then
    python Database.py
    python web_scraping.py
fi