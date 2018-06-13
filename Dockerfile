FROM python:3.6

COPY . /dp-conceptual-search
WORKDIR /dp-conceptual-search

# Install mongo - NB: This is a temporary step until we implement integration tests properly in CI
RUN apt-get update && apt-get install -y mongodb

# Start mongo
RUN mkdir -p /data/db
RUN chown -R mongodb:mongodb /data/db
#RUN mongod --fork --logpath /var/log/mongod.log --dbpath /data/db

ENV MONGO_BIND_ADDR=mongodb://0.0.0.0:27017

# Build the app and run the tests
RUN make build test clean

#ENTRYPOINT ["python"]
#CMD ["manager.py"]

CMD ./start.sh