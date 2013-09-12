#!/usr/bin/env python

from tools.sslconfparser import scp

try:
    from OpenSSL import crypto, SSL
    from socket import gethostname
    from pprint import pprint
    from time import gmtime, mktime, time
    from os.path import exists, join
    import sys
except ImportError:
    raise Exception("PyOpenSSL not installed.  Please install via pip install pyopenssl")

try:
    CN = sys.argv[1]
except:
    raise Exception("Please run as %s <common name/CN> [openssl.cnf file]" % sys.argv[0])

try:
    CNF = sys.argv[2]
except:
    print "> No openssl.cnf file provided.  Attempting to use /etc/ssl/openssl.cnf"
    CNF = "/etc/ssl/openssl.cnf"

print "> Attempting to read SSL config file..."
konf = scp(conf_file=CNF)

try:
    print "> Loaded organization name:",konf['0.organizationName_default']
except:
    raise Exception("Unable to parse %s.  Please make sure %s has read access to it." % (CNF, sys.argv[0]))

CERT_FILE = "%s.crt" % CN
KEY_FILE = "%s.key" % CN

C_F = join(".", CERT_FILE)
K_F = join(".", KEY_FILE)

if not exists(C_F) or not exists(K_F):
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    
    cert = crypto.X509()
    issuer = crypto.X509()
    
    issuer.get_subject().C = konf['countryName_default']
    issuer.get_subject().ST = konf['stateOrProvinceName_default']
    issuer.get_subject().L = konf['localityName']
    issuer.get_subject().O = konf['0.organizationName_default']
    issuer.get_subject().OU = konf['organizationalUnitName']
    issuer.get_subject().CN = CN
    
    cert.set_serial_number(int(time()))
    
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(315360000)
    
    cert.set_issuer(issuer.get_subject())
    
    cert.set_pubkey(k)
    
    cert.sign(k, 'sha1')
    
    open(C_F, "wt").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    open(K_F, "wt").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    
    print "> Wrote certificate to %s and key to %s" % (C_F, K_F)
else:
    print "> Not able to create a certificate.  %s.crt or %s.key exists" % (CN, CN)
