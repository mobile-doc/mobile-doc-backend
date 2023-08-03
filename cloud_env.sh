printenv > .env

echo "_PROJECT_NAME = $_PROJECT_NAME"

sed -i 's/%PROJECT_NAME%/'$PROJECT_NAME'/g' app.yaml

cat app.yaml