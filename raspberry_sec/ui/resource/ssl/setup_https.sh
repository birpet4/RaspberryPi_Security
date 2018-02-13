#!/bin/bash

openssl req -x509 -sha512 -newkey rsa:2048 -keyout ca.key -out ca.crt -days 365 -nodes

chmod 400 ca.*