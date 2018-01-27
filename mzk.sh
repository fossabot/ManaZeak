#!/bin/bash

if [ $# -eq 0 ]; then
      echo -e "\e[31mERROR: No arguments supplied.\e[39m"
      echo -e "Script usage: ./mzk.sh --help"

elif [ $1 = "--help" ] || [ $1 = "-h" ]; then
      printf "Usage: ./mzk.sh <command>\n"
      printf "Where <command> is one of:\n"
      printf "    build, dev, prod, stop\n\n"
      printf "./mzk.sh build     Build ManaZeak\n"
      printf "./mzk.sh dev       Run a dev environment\n"
      printf "./mzk.sh prod      Run a production environment\n"
      printf "./mzk.sh stop      Stop ManaZeak application\n\n"
      printf "./mzk.sh --help    Display the command usage (or -h)\n\n"
      printf "ManaZeak@0.1.0\n"

  elif [ $1 = "build" ]; then
      eval "docker-compose build"
      eval "npm install"

elif [ $1 = "dev" ]; then
    eval "docker-compose up -d"
    eval "npm run dev"

elif [ $1 = "prod" ]; then
    eval "docker-compose up -d"
    eval "npm run prod"

elif [ $1 = "stop" ]; then
    eval "docker stop manazeak_nginx manazeak_app manazeak_postgresql manazeak_moodbar manazeak_syncthing"

else
    echo -e "\e[31mERROR: Your argument is invalid.\e[39m"
    echo -e "Script usage: ./mzk.sh --help"

fi
