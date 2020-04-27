import netrc


def retrieve_from_netrc(machine):
    login = netrc.netrc().authenticators(machine)
    if not login:
        raise netrc.NetrcParseError('No authenticators for %s' % machine)
    return login
