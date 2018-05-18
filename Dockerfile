FROM python:3.6

COPY . /dp-conceptual-search
WORKDIR /dp-conceptual-search

RUN pip install Cython pybind11
RUN cd lib/fastText/ && python setup.py install
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["manager.py"]
