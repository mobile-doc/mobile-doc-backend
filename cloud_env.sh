printenv > .env

echo "_PROJECT_NAME = $_PROJECT_NAME"

sed -i 's/%_PROJECT_NAME%/'$_PROJECT_NAME'/g' app.yaml

cat app.yaml