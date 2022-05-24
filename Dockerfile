FROM python:3

RUN pip install --upgrade pip

RUN groupadd --gid 5000 newuser \
&& useradd --home-dir /home/newuser --create-home --uid 5000 \
--gid 5000 --shell /bin/sh --skel /dev/null newuser

USER newuser

ENV PATH="/home/newuser/.local/bin:${PATH}"

WORKDIR /home/newuser/app

COPY --chown=newuser:newuser requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt

COPY --chown=newuser:newuser . .
RUN pip install --user .
RUN chmod +x ./run_all.sh
RUN mkdir test/results

ENTRYPOINT [ "./run_all.sh" ]