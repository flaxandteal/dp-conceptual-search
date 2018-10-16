FROM python:3.6

COPY . /dp-conceptual-search
WORKDIR /dp-conceptual-search

# Build the app
RUN make build

ENTRYPOINT ["python"]
CMD ["manager.py"]
