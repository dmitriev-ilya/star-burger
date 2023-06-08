#!/bin/bash
set -Eeuo pipefail

/usr/bin/git -C ./star-burger pull
./star-burger/venv/bin/pip install -r ./star-burger/requirements.txt
./star-burger/venv/bin/python3 ./star-burger/manage.py migrate
./star-burger/venv/bin/python3 ./star-burger/manage.py collectstatic --noinput
npm --prefix ./star-burger/ ci --dev
./star-burger/node_modules/.bin/parcel build ./star-burger/bundles-src/index.js --dist-dir bundles --public-url="./"
systemctl daemon-reload
systemctl restart starburger
systemctl reload nginx

source ./star-burger/.env
git_commit=$(/usr/bin/git -C ./star-burger rev-parse HEAD)

curl -H "X-Rollbar-Access-Token:$ROLLBAR_TOKEN" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy'\
 -d '{"environment":"'$ROLLBAR_ENVIRONMENT'", "revision":"'$git_commit'", "rollbar_name":"'$ROLLBAR_NAME'", "local_username":"'$USER'", "comment": "", "status": "succeeded"}'

echo
echo "The deployment was successful!"
