import os, paramiko


class SSH:
    def __init__(self, bit_size, _dir):
        if bit_size in [1024, 2048, 4096]:
            self.key_file = f"{_dir}/id_rsa"
            self.bit_size = bit_size
            self.key = paramiko.RSAKey.generate(bit_size)
        else:
            raise Exception("bit_size should be a value of [1024, 2048, 4096]")

    def load_keys(self):
        # save private key
        with open(self.key_file, 'w') as private_key_file:
            self.key.write_private_key(private_key_file)            
        os.chmod(self.key_file, 0o600) # set permissions for the private key file
        # return public key
        return f"{self.key.get_name()} {self.key.get_base64()}"