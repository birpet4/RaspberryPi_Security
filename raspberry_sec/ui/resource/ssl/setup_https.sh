#!/bin/bash

# README:
#
# Run this script as root !
#

# Clean-up
chmod 700 root* server* v3*
rm root* server* v3*

# Root CA
openssl genrsa -out rootCA.key 2048
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 365 -out rootCA.pem -subj "/C=HU/ST=Hungary/L=Budapest/O=PCA CA Corp./CN=ca.pca.com/emailAddress=info@ca.pca.com/OU=CAIssue"

# Server CSR config
echo "[req]" > server.csr.config
echo "default_bits=2048" >> server.csr.config
echo "prompt=no" >> server.csr.config
echo "default_md=sha256" >> server.csr.config
echo "distinguished_name=dn" >> server.csr.config
echo "[dn]" >> server.csr.config
echo "C=HU" >> server.csr.config
echo "ST=Hungary" >> server.csr.config
echo "L=Budapest" >> server.csr.config
echo "O=PCA Corp." >> server.csr.config
echo "OU=HomeSec" >> server.csr.config
echo "emailAddress=info@pca.com" >> server.csr.config
echo "CN=localhost" >> server.csr.config

echo "authorityKeyIdentifier=keyid,issuer" > v3.ext
echo "basicConstraints=CA:FALSE" >> v3.ext
echo "keyUsage=digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment" >> v3.ext
echo "subjectAltName=@alt_names" >> v3.ext
echo "[alt_names]" >> v3.ext
echo "DNS.1=localhost" >> v3.ext

# Server Cert
openssl req -new -sha256 -nodes -out server.csr -newkey rsa:2048 -keyout server.key -config server.csr.config
openssl x509 -req -in server.csr -CA rootCA.pem -CAkey rootCA.key -CAcreateserial -out server.crt -days 500 -sha256 -extfile v3.ext

# Read-only
chmod 444 root* server* v3*