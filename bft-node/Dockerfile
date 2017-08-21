FROM debian:8

RUN echo "root:bigfoot1" | chpasswd

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
	iproute \
	net-tools \
	openssh-server \
	isc-dhcp-server \
	isc-dhcp-client \
	procps \
	iptables \
	lighttpd \
	tinyproxy \
	curl \
	apache2-utils \
	nmap \
	pppoe \
	tftpd-hpa \
	tcpdump \
	iperf \
	iperf3 \
	netcat

RUN mkdir /var/run/sshd
RUN sed -i 's/PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config

EXPOSE 22
