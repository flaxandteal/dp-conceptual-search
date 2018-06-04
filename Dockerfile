FROM python:3.6

COPY . /dp-conceptual-search
WORKDIR /dp-conceptual-search

RUN make build

ENTRYPOINT ["python"]
CMD ["manager.py"]
