docker run --name photo-db \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=photo_app \
  -e MYSQL_USER=user \
  -e MYSQL_PASSWORD=password \
  -p 13316:3306 \
  -v /Users/teriri/WIP_CODE/CSC184/PhotoApp/Database:/var/lib/mysql \
  -d mariadb:latest