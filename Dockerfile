FROM python:3.6.8

COPY . /dp-conceptual-search
WORKDIR /dp-conceptual-search

# Build the app
RUN make build clean

ENTRYPOINT ["python"]
CMD ["manager.py"]
