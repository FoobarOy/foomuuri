# Installation

The recommended way to install Foomuuri is through your Linux distribution's
package manager, using the instructions for your platform below.

For a sample configuration, see the [host firewall
example](example/host-firewall.md), which documents a typical
`/etc/foomuuri/foomuuri.conf` file.


## Fedora, RHEL and CentOS Stream

Foomuuri is included in Fedora and EPEL.

```sh
dnf install foomuuri foomuuri-firewalld
```

Continue with [post-installation configuration](#post-installation-configuration).


## Debian and Ubuntu

Foomuuri is included in Debian sid, forky, and trixie (13), as well as
bookworm-backports (12), and in Ubuntu 23.10 (Mantic) and 24.04 (Noble).

```sh
apt install foomuuri foomuuri-firewalld
```

Continue with [post-installation configuration](#post-installation-configuration).


## Arch Linux

Foomuuri is available in the Arch User Repository (AUR).

```sh
# Build and install the package
git clone https://aur.archlinux.org/foomuuri.git
cd foomuuri
makepkg
pacman -U foomuuri-*-x86_64.pkg.tar.zst
```

Continue with [post-installation configuration](#post-installation-configuration).


## Building from Source

Source tarballs are available on the
[releases page](https://github.com/FoobarOy/foomuuri/releases).

**Requirements**

- `nftables` version 1.0.0 or higher, built with JSON support
- `python` version 3.9 or higher

**Recommended**

- `python3-dbus` and `python3-gobject` (`python3-gi` on some distributions)
  — required for D-Bus support

**Optional**

- `python3-systemd`
- `python3-urllib3`
- `python3-lxml`

```sh
# Extract the source
tar xf foomuuri-0.??.tar.gz
cd foomuuri-0.??

# Install to the root filesystem
make install DESTDIR=/
systemctl daemon-reload
sysctl --system
```

Continue with [post-installation configuration](#post-installation-configuration).


## Post-installation configuration

These steps apply regardless of how Foomuuri was installed.

1.  Configure and validate:

    ```sh
    $EDITOR /etc/foomuuri/foomuuri.conf
    foomuuri check
    ```

    For a sample configuration, see the
	[host firewall example](example/host-firewall.md).


2.  Disable and stop any existing firewall service, for example:

    ```sh
	systemctl disable --now ferm.service
    systemctl disable --now firehol.service
    systemctl disable --now firewalld.service
    systemctl disable --now netfilter-persistent.service  
    systemctl disable --now nftables.service
    systemctl disable --now shorewall-init.service
    systemctl disable --now shorewall.service
    systemctl disable --now shorewall6.service
    systemctl disable --now ufw.service
    nft flush ruleset
    ```

3.  Start Foomuuri:

    ```sh
    systemctl start foomuuri.service
    ```

4.  Verify firewall logging in the system journal:

    ```sh
    journalctl --follow --dmesg
    ```

5.  Enable Foomuuri at boot, once you have confirmed it is working correctly:

    ```sh
    systemctl enable foomuuri.service
    ```
