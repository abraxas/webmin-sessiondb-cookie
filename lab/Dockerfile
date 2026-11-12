FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C \
    WEBMIN_CONFIG=/etc/webmin \
    WEBMIN_VAR=/var/webmin \
    PERLLIB=/usr/share/webmin

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        hostname \
        libio-pty-perl \
        libnet-ssleay-perl \
        openssl \
        perl \
        shared-mime-info \
        unzip \
    && rm -rf /var/lib/apt/lists/*

COPY . /usr/share/webmin
WORKDIR /usr/share/webmin

RUN set -eux; \
    export config_dir=/etc/webmin \
        var_dir=/var/webmin \
        perl=/usr/bin/perl \
        autoos=3 \
        os_type=debian-linux \
        os_version=12 \
        real_os_type="Debian Linux" \
        real_os_version=12 \
        port=10000 \
        login=root \
        password=labroot \
        ssl=0 \
        atboot=0 \
        nostart=1 \
        noportcheck=1; \
    /bin/sh ./setup.sh; \
    grep -q '^ssl=0' /etc/webmin/miniserv.conf; \
    sed -i 's/^ipv6=.*/ipv6=0/' /etc/webmin/miniserv.conf; \
    mkdir -p /var/mail /var/spool/mail

LABEL version="2.670" \
      git_commit="3a2b2b8671c0669c129f5275b3dd1853106ae02b" \
      lab="WEBMIN-H27-SESSIONDB"

EXPOSE 10000
CMD ["/usr/bin/perl", "/usr/share/webmin/miniserv.pl", "--nofork", "/etc/webmin/miniserv.conf"]
