FROM python:3.9

RUN groupadd --gid 5000 eghbalaz \
&& useradd --home-dir /home/eghbalaz --create-home --uid 5000 \
--gid 5000 --shell /bin/sh --skel /dev/null eghbalaz

USER eghbalaz

ENV PATH="/home/eghbalaz/.local/bin:${PATH}"

WORKDIR /home/eghbalaz/app

RUN pip install --upgrade pip setuptools wheel

COPY --chown=eghbalaz:eghbalaz requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=eghbalaz:eghbalaz . .
RUN pip install .
RUN chmod +x ./run_all.sh
RUN mkdir test/results

ENTRYPOINT [ "./run_all.sh" ]