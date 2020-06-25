ARG PYTHON_VERSION="3.6"
FROM python:${PYTHON_VERSION}

LABEL maintainer="Alain Sanchez <brazzisoft.com@gmail.com>" \
      company="BRAZZISOFT"  \
      project="udemy-dl"

ENV PYTHONUNBUFFERED 1
ENV PYTHONOPTIMIZE 1
ENV UDEMY_USER udemy
ENV UDEMY_USER_UID 1000
ENV UDEMY_GROUP udemy
ENV UDEMY_GROUP_GID 1000
ENV APP_HOME /udemy-dl
ENV SRC_HOME $APP_HOME/src
ENV VENV_HOME $APP_HOME/venv
ENV COURSE_HOME $SRC_HOME/courses

ARG UDEMY_COURSE_URL=""
ENV UDEMY_COURSE_URL ${UDEMY_COURSE_URL}
ARG UDEMYDL_ARGS=""
ENV UDEMYDL_ARGS ${UDEMYDL_ARGS}


# System Configuration
# .: 1. Install required packages
RUN set -eux; \
    apt-get -qq update; \
    apt-get -qqy install  \
        apt-utils \
        python-virtualenv \
        build-essential; \
    rm -rf /var/lib/apt/lists/*;

# .: 2. Create file system. Add application user and group
RUN set -eux; \
    groupadd -r -g $UDEMY_GROUP_GID $UDEMY_GROUP; \
    useradd -r -u $UDEMY_USER_UID -d $APP_HOME -g $UDEMY_GROUP $UDEMY_USER; \
    mkdir -p $COURSE_HOME; \
    mkdir -p $VENV_HOME; \
    chown -R $UDEMY_USER:$UDEMY_GROUP $SRC_HOME $VENV_HOME;


# Application Configuration
# .: 1. Set the workdir to the APP_HOME
WORKDIR $APP_HOME
# .: 2. Define virtualenv environment
RUN virtualenv -p python $VENV_HOME
# .: 3. Copy requirements and install them
COPY ./requirements.txt $SRC_HOME
SHELL ["/bin/bash", "-c"]
RUN source $VENV_HOME/bin/activate && pip install -r $SRC_HOME/requirements.txt
# .: 4. Copy application
COPY ./udemy $SRC_HOME/udemy/
COPY ./udemy-dl.py $SRC_HOME
# .: 5. Setting up the docker entrypoint file
COPY ./.container/udemy-dl/docker-entrypoint.sh /docker-entrypoint.sh
# .: 6. Making sure all the files/folders are owned by UDEMY_USER
RUN chown -R $UDEMY_USER:$UDEMY_GROUP $APP_HOME && \
    chmod +x /docker-entrypoint.sh && \
    chown $UDEMY_USER:$UDEMY_GROUP /docker-entrypoint.sh
# .: 7. Switch context to UDEMY_USER
USER $UDEMY_USER

# Container Metadata definition
VOLUME ["$COURSE_HOME"]

# .: Invoking Default entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]