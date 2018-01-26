#!/bin/bash

if [ $1 = "dev" ]; then
$command = `docker-compose up -d`
echo "$command"
$command = `npm run dev`
echo "$command"

elif [ $1 = "prod" ]; then
$command = `docker-compose up -d`
echo "$command"
$command = `npm run prod`
echo "$command"

elif [ $1 = "init" ]; then
$command = `docker-compose build`
echo "$command"
$command = `npm install`
echo "$command"

fi
