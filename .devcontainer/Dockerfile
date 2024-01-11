FROM python:3.11

RUN apt-get update && apt-get -y install swig libpcsclite-dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USER=compiler

RUN useradd --create-home --shell /bin/bash $USER && \
    chown -R $USER /home/$USER

USER $USER
ENV PATH "$PATH:/home/$USER/.local/bin"
WORKDIR /home/$USER/admin

RUN python -m pip install --upgrade pip

COPY .git .git
COPY compiler_admin compiler_admin
COPY pyproject.toml pyproject.toml
RUN pip install -e .[dev,test]

CMD ["sleep", "infinity"]
