FROM amazonlinux

LABEL description="GFortran & netCDF & FCM Make on Amazon Linux 2" \
      maintainer="matthew.shin@metoffice.gov.uk" \
      version="0.1"

# Dependencies for FCM Make.
RUN yum -y update \
    && yum -y install curl gcc-gfortran glibc-static gzip perl-core tar

# Dependencies for netCDF libraries.
# Note: NetCDF libraries on EPEL do not work with modern GFortran,
#       so building from source here.
RUN yum -y install libcurl-devel make m4 zlib-devel \
    && yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm \
    && yum -y install hdf5 hdf5-devel hdf5-static

# Install FCM Make
WORKDIR /opt
ENV FCM_VN=2019.09.0
RUN curl -L "https://github.com/metomi/fcm/archive/${FCM_VN}.tar.gz" | tar -xz
WORKDIR /usr/local/bin
RUN echo -e '#!/bin/sh'"\n"'exec /opt/fcm-'"${FCM_VN}"'/bin/fcm "$@"' >'fcm' \
    && chmod +x 'fcm'

# Build and install netCDF libraries.
WORKDIR /opt
ENV NC_VN=4.6.1
ENV NF_VN=4.4.4
RUN curl -L "https://github.com/Unidata/netcdf-c/archive/v${NC_VN}.tar.gz" | tar -xz
RUN curl -L "https://github.com/Unidata/netcdf-fortran/archive/v${NF_VN}.tar.gz" | tar -xz
WORKDIR /opt/netcdf-c-${NC_VN}
ENV NCDIR=/usr/local
RUN ./configure --prefix="${NCDIR}" && make check install && nc-config --all
WORKDIR /opt/netcdf-fortran-${NF_VN}
ENV LD_LIBRARY_PATH=${NCDIR}/lib
RUN env CPPFLAGS=-I${NCDIR}/include LDFLAGS=-L${NCDIR}/lib ./configure --prefix="${NCDIR}" \
    && make check install && nf-config --all

WORKDIR /opt
