FROM amazonlinux:1

LABEL description="GFortran & netCDF & FCM Make on Amazon Linux 1" \
      maintainer="matthew.shin@metoffice.gov.uk" \
      version="0.1"

RUN yum -y update && yum config-manager --enable epel
RUN yum -y install gcc-gfortran glibc-static hdf5-static m4 netcdf-static perl-core zlib-static

# Install FCM Make
WORKDIR /opt
ENV FCM_VN=2019.09.0
RUN curl -L "https://github.com/metomi/fcm/archive/${FCM_VN}.tar.gz" | tar -xz
WORKDIR /usr/local/bin
RUN echo -e '#!/bin/sh'"\n"'exec /opt/fcm-'"${FCM_VN}"'/bin/fcm "$@"' >'fcm' \
    && chmod +x 'fcm'
