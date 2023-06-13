#!/bin/bash
set -Eeuo pipefail

/usr/bin/git -C ./ pull
./venv/bin/pip install -r ./requirements.txt
./venv/bin/python3 ./manage.py migrate --noinput
./venv/bin/python3 ./manage.py collectstatic --noinput
npm --prefix ./ ci --dev
./node_modules/.bin/parcel build ./bundles-src/index.js --dist-dir bundles --public-url="./"
systemctl daemon-reload
systemctl restart starburger
systemctl reload nginx

source ./.env
git_commit=$(/usr/bin/git -C ./ rev-parse HEAD)

curl -H "X-Rollbar-Access-Token:$ROLLBAR_TOKEN" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy'\
 -d '{"environment":"'$ROLLBAR_ENVIRONMENT'", "revision":"'$git_commit'", "rollbar_name":"'$ROLLBAR_NAME'", "local_username":"'$USER'", "comment": "", "status": "succeeded"}'

echo
echo "The deployment was successful!"
