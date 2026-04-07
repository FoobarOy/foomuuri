# Getting Started

The easiest way to install Foomuuri is to use packages from your Linux
distribution.


## Fedora, RHEL9, CentOS Stream

Foomuuri is included to Fedora 38 (and newer) and to EPEL9.

```
# Install packages
dnf install foomuuri foomuuri-firewalld

# Configure Foomuuri and verify it
$EDITOR /etc/foomuuri/foomuuri.conf
foomuuri check

# Disable and stop current firewall, for example:
systemctl disable firewalld.service
systemctl disable shorewall.service
systemctl disable shorewall6.service
systemctl disable shorewall-init.service
nft flush ruleset

# Enable and start Foomuuri
systemctl enable foomuuri.service
systemctl start foomuuri.service

# Check journal log for Foomuuri logging
journalctl --follow --dmesg
```


## Debian, Ubuntu

Foomuuri is include to Debian 12 backports (Bookworm), Debian Unstable
(Sid), Ubuntu 23.10 (Mantic) and Ubuntu 24.04 (Noble).

```
# Install packages
apt install foomuuri foomuuri-firewalld

# Configure Foomuuri and verify it
$EDITOR /etc/foomuuri/foomuuri.conf
foomuuri check

# Disable and stop current firewall, for example:
systemctl disable firewalld.service
systemctl disable shorewall.service
systemctl disable shorewall6.service
systemctl disable shorewall-init.service
nft flush ruleset

# Enable and start Foomuuri
systemctl enable foomuuri.service
systemctl start foomuuri.service

# Check journal log for Foomuuri logging
journalctl --follow --dmesg
```


## Arch Linux

Foomuuri is included to Arch User Repository (AUR).

```
# Build and install packages
git clone https://aur.archlinux.org/foomuuri.git
cd foomuuri
makepkg
pacman -U foomuuri-*-x86_64.pkg.tar.zst

# Configure Foomuuri and verify it
$EDITOR /etc/foomuuri/foomuuri.conf
foomuuri check

# Disable and stop current firewall, for example:
systemctl disable firewalld.service
systemctl disable shorewall.service
systemctl disable shorewall6.service
systemctl disable shorewall-init.service
nft flush ruleset

# Enable and start Foomuuri
systemctl enable foomuuri.service
systemctl start foomuuri.service

# Check journal log for Foomuuri logging
journalctl --follow --dmesg
```


## Source code

Source code tarball is available in
[releases page](https://github.com/FoobarOy/foomuuri/releases).

Foomuuri depends on `nftables` (version 1.0.0 or higher), `python`
(version 3.9 or higher), `python3-dbus` and `python3-gobject` (called
`python3-gi` in some distributions). Optionally Foomuuri will use
`python3-systemd`, `python3-requests` and `python3-lxml` if they are
available. Install those dependencies first. Older version of `nftables` will
work if [a patch](https://github.com/FoobarOy/foomuuri/issues/27) is applied
to Foomuuri.

```
# Untar source
tar xf foomuuri-0.??.tar.gz
cd foomuuri-0.??

# Install it to root filesystem
sudo make install DESTDIR=/
sudo systemctl daemon-reload

# Configure Foomuuri and verify it
$EDITOR /etc/foomuuri/foomuuri.conf
foomuuri check

# Disable and stop current firewall, for example:
systemctl disable firewalld.service
systemctl disable shorewall.service
systemctl disable shorewall6.service
systemctl disable shorewall-init.service
nft flush ruleset

# Enable and start Foomuuri
systemctl enable foomuuri.service
systemctl start foomuuri.service

# Check journal log for Foomuuri logging
journalctl --follow --dmesg
```
