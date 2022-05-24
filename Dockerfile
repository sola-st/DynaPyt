FROM python:3

WORKDIR /usr/src/app

RUN pip install --upgrade pip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install .
RUN chmod +x ./run_all.sh
RUN mkdir test/results

ENTRYPOINT [ "./run_all.sh" ]