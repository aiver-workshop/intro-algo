"""
Download gpg4win from https://www.gpg4win.org/about.html

After installation, you will have Kleopatra, a GUI to run various cryptographic actions.

Open Kleopatra -> Sign/Encrypt -> <select the file to encrypt> -> uncheck everything and only select
"Encrypt with password. Anyone you share the password with can read the data"

Also do "pip install python-gnupg"

PyCharm Note:
To get the password prompt, go to 'Edit Configurations' and then select 'Emulate terminal in output console'

"""
import getpass
import gnupg


def decrypt_file(_encrypted_file):
    p = getpass.getpass(prompt='Your password? ')
    print('Password entered.')

    gpg = gnupg.GPG()
    with open(_encrypted_file, 'rb') as f:
        return str(gpg.decrypt_file(f, passphrase=p))


if __name__ == '__main__':
    encrypted_file = 'c:/temp/.secrets.gpg'
    secrets = decrypt_file(encrypted_file)
    data = secrets.splitlines()
    print(data)

