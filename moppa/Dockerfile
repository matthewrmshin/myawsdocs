FROM amazonlinux

LABEL description="GFortran & netCDF & FCM Make on Amazon Linux 2" \
      maintainer="matthew.shin@metoffice.gov.uk" \
      version="0.1"

# Dependencies for FCM Make.
RUN yum -y update && yum -y install curl gcc-gfortran gzip perl-core tar

# Install FCM Make
WORKDIR /opt
ENV FCM_VN=2019.09.0
RUN curl -L "https://github.com/metomi/fcm/archive/${FCM_VN}.tar.gz" | tar -xz
WORKDIR /usr/local/bin
RUN echo -e '#!/bin/sh'"\n"'exec /opt/fcm-${FCM_VN}/bin/fcm "$@"' >'fcm' \
    && chmod +x 'fcm'

WORKDIR /opt
