FROM python:3.9

ARG repo

WORKDIR /DynaPyt

RUN pip install --upgrade pip setuptools wheel

COPY . .

RUN pip install .
