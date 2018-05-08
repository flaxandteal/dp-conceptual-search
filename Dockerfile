FROM python:3.6
COPY . /dp-conceptual-search
WORKDIR /dp-conceptual-search
RUN pip install -r requirements.txt

EXPOSE 5050

ENTRYPOINT ["python"]
CMD ["manager.py"]
#CMD ["./run_gunicorn.sh"]