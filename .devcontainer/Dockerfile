FROM python:3.12-bookworm

# declare default build args for later
ARG PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USER=compiler \
    USER_UID=1000 \
    USER_GID=1000

# set env vars for the user, including HOME
ENV PYTHONUNBUFFERED=${PYTHONUNBUFFERED} \
    PYTHONDONTWRITEBYTECODE=${PYTHONDONTWRITEBYTECODE} \
    HOME=/home/${USER} \
    USER=${USER} \
    PATH="/${USER}/.local/bin:/home/$USER/.config/compiler-admin/gyb:$PATH" \
    # update env for local pip installs
    # see https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUSERBASE
    # since all `pip install` commands are in the context of $USER
    # $PYTHONUSERBASE is the location used by default
    PYTHONUSERBASE="/${USER}/.local" \
    # where to store the pip cache (use the default)
    # https://pip.pypa.io/en/stable/cli/pip/#cmdoption-cache-dir
    PIP_CACHE_DIR="/${USER}/.cache/pip"

# install apt packages using the archives and lists cache
RUN --mount=type=cache,id=apt-archives,sharing=locked,target=/var/cache/apt/archives \
    --mount=type=cache,id=apt-lists,sharing=locked,target=/var/lib/apt/lists \
    apt-get update && \
    apt-get install -y swig libpcsclite-dev

RUN useradd --create-home --shell /bin/bash $USER
RUN mkdir -p /$USER && chown -R $USER:$USER /home/$USER /$USER

USER $USER
RUN mkdir -p /home/$USER/.config/compiler-admin
WORKDIR /home/$USER/compiler-admin
RUN git config --global --add safe.directory /home/$USER/compiler-admin

RUN python -m pip install --user --upgrade pip

COPY .git .git
COPY compiler_admin compiler_admin
COPY pyproject.toml pyproject.toml

RUN --mount=type=cache,id=pipcache,target=${PIP_CACHE_DIR},uid=${USER_UID},gid=${USER_GID} \
    pip install --user -e .[dev,test]

COPY docs/requirements.txt docs/requirements.txt

RUN --mount=type=cache,id=pipcache,target=${PIP_CACHE_DIR},uid=${USER_UID},gid=${USER_GID} \
    pip install --user -r docs/requirements.txt

CMD ["sleep", "infinity"]
