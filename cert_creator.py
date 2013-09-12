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

TYPE_RSA = crypto.TYPE_RSA
TYPE_DSA = crypto.TYPE_DSA

def createKeyPair(type, bits):
    """
    Create a public/private key pair.

    Arguments: type - Key type, must be one of TYPE_RSA and TYPE_DSA
               bits - Number of bits to use in the key
    Returns:   The public/private key pair in a PKey object
    """
    pkey = crypto.PKey()
    pkey.generate_key(type, bits)
    return pkey

def createCertRequest(pkey, digest="md5", **name):
    """
    Create a certificate request.

    Arguments: pkey   - The key to associate with the request
               digest - Digestion method to use for signing, default is md5
               **name - The name of the subject of the request, possible
                        arguments are:
                          C     - Country name
                          ST    - State or province name
                          L     - Locality name
                          O     - Organization name
                          OU    - Organizational unit name
                          CN    - Common name
                          emailAddress - E-mail address
    Returns:   The certificate request in an X509Req object
    """
    req = crypto.X509Req()
    subj = req.get_subject()

    for (key,value) in name.items():
        setattr(subj, key, value)

    req.set_pubkey(pkey)
    req.sign(pkey, digest)
    return req

def createCertificate(req, (issuerCert, issuerKey), serial, (notBefore, notAfter), digest="md5"):
    """
    Generate a certificate given a certificate request.

    Arguments: req        - Certificate reqeust to use
               issuerCert - The certificate of the issuer
               issuerKey  - The private key of the issuer
               serial     - Serial number for the certificate
               notBefore  - Timestamp (relative to now) when the certificate
                            starts being valid
               notAfter   - Timestamp (relative to now) when the certificate
                            stops being valid
               digest     - Digest method to use for signing, default is md5
    Returns:   The signed certificate in an X509 object
    """
    cert = crypto.X509()
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(notBefore)
    cert.gmtime_adj_notAfter(notAfter)
    cert.set_issuer(issuerCert.get_subject())
    cert.set_subject(req.get_subject())
    cert.set_pubkey(req.get_pubkey())
    cert.sign(issuerKey, digest)
    return cert
    
if not exists(C_F) or not exists(K_F):
    k = createKeyPair(crypto.TYPE_RSA, 2048)
    req = createCertRequest(k, C=konf['countryName_default'],
        ST=konf['stateOrProvinceName_default'],
        L=konf['localityName'],
        O=konf['0.organizationName_default'],
        OU=konf['organizationalUnitName'],
        CN=CN)
    cert = createCertificate(req, (req, k), 0, (0, 60*60*24*365*5))
    
    open(C_F, "wt").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    open(K_F, "wt").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    
    print "> Wrote certificate to %s and key to %s" % (C_F, K_F)
else:
    print "> Not able to create a certificate.  %s.crt or %s.key exists" % (CN, CN)
