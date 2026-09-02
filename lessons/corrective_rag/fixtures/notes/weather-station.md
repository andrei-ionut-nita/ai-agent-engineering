# Project Aurora

Project Aurora is a personal weather station built from a Raspberry Pi
and a set of outdoor sensors. It logs temperature, humidity, and wind
speed every five minutes to a local database. The project started in
March 2024 as a way to learn embedded electronics.

The Raspberry Pi runs headless, with no monitor attached. It connects
to the sensors over a short ribbon cable and writes each reading to a
SQLite file on its SD card. Once a day, a small script uploads that
file to cloud storage as a backup.

The most failure-prone part of the whole setup has been the wind speed
sensor: its bearings need re-oiling every few months, or the readings
start drifting low.
