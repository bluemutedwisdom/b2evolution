#!/usr/bin/python
"""Set b2evolution admin password and email

Option:
    --pass=     unless provided, will ask interactively
    --email=    unless provided, will ask interactively

"""

import sys
import getopt
import inithooks_cache
import hashlib
from uuid import uuid4
from random import SystemRandom
from string import ascii_letters, digits

from dialog_wrapper import Dialog
from mysqlconf import MySQL, escape_chars

random = SystemRandom()

def randomkey():
    return str(uuid4()).replace('-' ,'')

def usage(s=None):
    if s:
        print >> sys.stderr, "Error:", s
    print >> sys.stderr, "Syntax: %s [options]" % sys.argv[0]
    print >> sys.stderr, __doc__
    sys.exit(1)

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'email='])
    except getopt.GetoptError, e:
        usage(e)

    password = ""
    email = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--email':
            email = val

    if not password:
        d = Dialog('TurnKey Linux - First boot configuration')
        password = d.get_password(
            "b2evolution Password",
            "Enter new password for the b2evolution 'admin' account.")

    if not email:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        email = d.get_email(
            "b2evolution Email",
            "Enter email address for the b2evolution 'admin' account.",
            "admin@example.com")

    inithooks_cache.write('APP_EMAIL', email)

    salt = ''.join(random.choice(ascii_letters+digits) for i in range(8)) 
    hash = hashlib.md5(salt+password).digest()

    m = MySQL()
    username = 'admin'
    m.execute('UPDATE b2evolution.users SET user_pass=\"%s\", user_email=\"%s\", user_unsubscribe_key=\"%s\", user_salt=\"%s\" WHERE user_login=\"%s\";' % \
	(escape_chars(hash), email, randomkey(), salt, username))


if __name__ == "__main__":
    main()

