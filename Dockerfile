FROM python:3.6

COPY . /dp-conceptual-search
WORKDIR /dp-conceptual-search
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["manager.py"]
