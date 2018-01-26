#!/bin/bash

echo $0

if [ $1 = "dev" ]
then
#command="npm run dev"
command=`ls -l`
echo "$command"

elif [ $1 = "prod" ]
then
echo npm run prod
echo "$command"

elif [ $1 = "init" ]
then
echo docker-compose build
echo npm install
echo docker-compose up -d
echo "$command"

fi

#npm install
#docker build
#docker compose up- d
