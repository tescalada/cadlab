FROM heroku/miniconda:3

RUN apt-get update -y && \
    apt-get install --no-install-recommends -y libgl1-mesa-glx libglu1-mesa npm && \
    apt-get clean

#RUN conda install -c conda-forge -c cadquery cadquery=2.1
RUN conda create -n cq -c default -c conda-forge -c cadquery python=3.8 cadquery=2.1 && \
    conda clean --all && \
    find / -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

# Grab requirements.txt.
ADD ./requirements.txt /tmp/requirements.txt

# Install dependencies
RUN bash -l -c ". /opt/conda/bin/activate cq && \
    pip install -qr /tmp/requirements.txt && \
    find / -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete"

# Add our code
ADD . /opt/webapp/
WORKDIR /opt/webapp

RUN useradd -m myuser
USER myuser

CMD bash -l -c ". /opt/conda/bin/activate cq && gunicorn --bind 0.0.0.0:$PORT app:app --log-file - "
