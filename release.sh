#!/bin/bash

cd AccSide/
# Execute your command

python manage.py migrate
python manage.py makesuperuser