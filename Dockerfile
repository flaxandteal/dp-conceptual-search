FROM python:3.6
#FROM sully0190/python-mongo:3.6

COPY . /dp-conceptual-search
WORKDIR /dp-conceptual-search

# Build the app
RUN make build clean

ENTRYPOINT ["python"]
CMD ["manager.py"]