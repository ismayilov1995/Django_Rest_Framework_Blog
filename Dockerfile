FROM python:3

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . /code/

RUN pip install -r requiretments.txt

EXPOSE 8000

CMD["gunicorn","--chdir","Django_Rest_Framework_Blog","--bind",":8000","blog.wsgi:application"]