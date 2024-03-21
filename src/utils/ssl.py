import tempfile
from ssl import SSLContext, PROTOCOL_TLS_CLIENT

def create_ssl_context(certFile: str, caFile: str, keyFile: str):
    
    with tempfile.NamedTemporaryFile() as cert_temp, \
        tempfile.NamedTemporaryFile() as key_temp, \
        tempfile.NamedTemporaryFile() as ca_temp:
        
        cert_temp.write(certFile.encode())
        key_temp.write(keyFile.encode())
        ca_temp.write(caFile.encode())
        
        cert_temp.flush()
        key_temp.flush()
        ca_temp.flush()
        
        ssl_context = SSLContext(PROTOCOL_TLS_CLIENT)
        ssl_context.load_cert_chain(certfile=cert_temp.name, keyfile=key_temp.name)
        ssl_context.load_verify_locations(cafile=ca_temp.name)
        
        return ssl_context
