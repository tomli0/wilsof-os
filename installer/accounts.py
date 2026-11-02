"""Shared desktop-username policy for installer preflight and provisioning."""
import re

# Base/desktop service identities must never become the administrator account.
# Keep package-account additions here, not in separate caller deny lists.
RESERVED_USERNAMES = frozenset({
    'root', 'bin', 'daemon', 'mail', 'ftp', 'http', 'nobody', 'dbus',
    'sys', 'sync', 'games', 'lp', 'news', 'uucp', 'uuidd', 'alpm',
    'avahi', 'avahi-autoipd', 'brltty', 'colord', 'cups', 'dhcpcd',
    'dnsmasq', 'flatpak', 'gdm', 'geoclue', 'git', 'greetd', 'greeter',
    'nm-openvpn', 'ntp', 'polkitd', 'rpc', 'rtkit', 'saned', 'sddm',
    'tss', 'usbmux', 'named', 'nbd', 'openvpn', 'partimag', 'pcscd', 'rpcuser',
})


def validate_username(username):
    """Reject malformed/service names before disk writes and at provisioning."""
    if (not isinstance(username, str)
            or not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', username)
            or username in RESERVED_USERNAMES or username.startswith('systemd-')):
        raise ValueError('Unsupported or reserved username')
