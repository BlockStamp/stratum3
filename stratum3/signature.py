#!/usr/bin/env python

import base64
import hashlib
import time
import ecdsa

import jsonical
import json


from stratum3 import exceptions


def get_SECP256k1():
    # secp256k1, http://www.oid-info.com/get/1.3.132.0.10
    _p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    _r = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    _b = 0x0000000000000000000000000000000000000000000000000000000000000007
    _a = 0x0000000000000000000000000000000000000000000000000000000000000000
    _Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    _Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
    curve_secp256k1 = ecdsa.ellipticcurve.CurveFp(_p, _a, _b)
    generator_secp256k1 = ecdsa.ellipticcurve.Point(curve_secp256k1, _Gx, _Gy, _r)
    oid_secp256k1 = (1, 3, 132, 0, 10)
    SECP256k1 = ecdsa.curves.Curve("SECP256k1", curve_secp256k1, generator_secp256k1,
                                   oid_secp256k1)

    # Register SECP256k1 to ecdsa library
    ecdsa.curves.curves.append(SECP256k1)
    return SECP256k1

SECP256k1 = get_SECP256k1()


def generate_keypair():
    private_key = ecdsa.SigningKey.generate(curve=SECP256k1)
    public_key = private_key.get_verifying_key()
    return private_key, public_key


def load_privkey_pem(filename):
    return ecdsa.SigningKey.from_pem(open(filename, 'r').read().strip())


def sign(privkey, data):
    hash = hashlib.sha256(data).digest()
    signature = privkey.sign_digest(hash, sigencode=ecdsa.util.sigencode_der)
    return base64.b64encode(signature)


def verify(pubkey, signature, data):
    hash = hashlib.sha256(data).digest()
    sign = base64.b64decode(signature)

    try:
        return pubkey.verify_digest(sign, hash, sigdecode=ecdsa.util.sigdecode_der)
    except:
        pass

    return False


def jsonrpc_dumps_sign(privkey, privkey_id, is_request, message_id, method='',
                       params=None, result=None, error=None):
    """Create the signature for given json-rpc
    data and returns signed json-rpc text stream"""

    params = params or []

    # Build data object to sign
    sign_time = int(time.time())
    data = dict(method=method, params=params,
                result=result, error=error, sign_time=sign_time)

    # Serialize data to sign and perform signing
    txt = jsonical.dumps(data)
    signature = sign(privkey, txt)
    
    # Reconstruct final data object and put signature
    data = dict(id=message_id, sign=signature, sign_algo='ecdsa;SECP256k1',
                sign_id=privkey_id, sign_time=sign_time)

    if is_request:
        _data = dict(method=method, params=params)
    else:
        _data = dict(result=result, error=error)
    data.update(_data)

    # Return original data extended with signature
    return jsonical.dumps(data)


def jsonrpc_loads_verify(pubkeys, txt):
    '''
        Pubkeys is mapping (dict) of sign_id -> ecdsa public key.
        This method deserialize provided json-encoded data, load signature ID, perform the lookup for public key
        and check stored signature of the message. If signature is OK, returns message data.
    '''
    data = json.loads(txt)
    signature_algo = data['sign_algo']
    signature_id = data['sign_id']
    signature_time = data['sign_time']
    
    if signature_algo != 'ecdsa;SECP256k1':
        raise exceptions.UnknownSignatureAlgorithmException(
            "%s is not supported" % signature_algo)
    
    try:
        pubkey = pubkeys[signature_id]
    except KeyError:
        raise exceptions.UnknownSignatureIdException(
            "Public key for '%s' not found" % signature_id)
    
    signature = data['sign']
    message_id = data['id']
    method = data.get('method', '')
    params = data.get('params', [])
    result = data.get('result', None)
    error = data.get('error', None)
    
    # Build data object to verify
    data = dict(method=method, params=params, result=result,
                error=error, sign_time=signature_time)
    txt = jsonical.dumps(data)
    
    if not verify(pubkey, signature, txt):
        raise exceptions.SignatureVerificationFailedException(
            "Signature doesn't match to given data")
    
    if method:
        # It's a request
        return dict(id=message_id, method=method, params=params)

    # It's aresponse
    return dict(id=message_id, result=result, error=error)


if __name__ == '__main__':
    (private, public) = generate_keypair()
    print(private.to_pem())
