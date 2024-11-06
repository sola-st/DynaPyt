FROM python:3.11-slim

ARG repo

WORKDIR /DynaPyt

RUN pip install --upgrade pip setuptools wheel

COPY . .

RUN pip install .
