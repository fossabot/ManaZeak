#!/bin/bash



if [ $1 = "dev" ]
then
#command="npm run dev"
command=`npm run dev`
echo "$command"

elif [ $1 = "prod" ]
then
command= `npm run prod`
echo "$command"

elif [ $1 = "init" ]
then
command= `docker-compose build`
command= `npm install`
command= `docker-compose up -d`
echo "$command"

fi

#npm install
#docker build
#docker compose up- d
