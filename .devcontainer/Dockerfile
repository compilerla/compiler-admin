FROM python:3.11

RUN apt-get update && apt-get -y install swig libpcsclite-dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USER=compiler

RUN useradd --create-home --shell /bin/bash $USER

USER $USER
RUN mkdir -p /home/$USER/.config/compiler-admin
ENV PATH="$PATH:/home/$USER/.local/bin:/home/$USER/.config/compiler-admin/gyb"
WORKDIR /home/$USER/compiler-admin

RUN python -m pip install --upgrade pip

COPY .git .git
COPY compiler_admin compiler_admin
COPY pyproject.toml pyproject.toml
RUN pip install -e .[dev,test]

USER root
RUN chown -R $USER:$USER /home/$USER
USER $USER

CMD ["sleep", "infinity"]
