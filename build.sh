docker build -t crotalpath .
docker rm crotalpath
docker create --name crotalpath -p 5000:5000 -t crotalpath