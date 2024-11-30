docker run --name ecopix_docker \
  -e DATABASE_URI="mysql+pymysql://user:password@localhost:13316/photo_app" \
  -p 15381:15381 \
  junyu07/ecopix_docker:latest


#  -d junyu07/ecopix_docker:latest
# docker run --name ecopix_docker \
#   -e DATABASE_URI=localhost \
#   -e DATABASE_HOST=mariadb \
#   -e DATABASE_PORT=13316 \
#   -e DATABASE_USER=user \
#   -e DATABASE_PASSWORD=password \
#   -e DATABASE_NAME=photo_app \
#   -p 15381:15381 
# #  -d junyu07/ecopix_docker:latest
