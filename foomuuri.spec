Name:           foomuuri
Version:        0.18
Release:        1%{?dist}
Summary:        Multizone bidirectional nftables firewall
License:        GPLv2+
URL:            https://github.com/FoobarOy/foomuuri
Source0:        https://github.com/FoobarOy/foomuuri/archive/v%{version}/foomuuri-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  make
BuildRequires:  systemd-rpm-macros
Requires:       nftables
Requires:       python3-dbus
Requires:       python3-gobject
Requires:       python3-requests
Requires:       python3-systemd
Recommends:     fping
Recommends:     (foomuuri-firewalld if NetworkManager)
%{?systemd_requires}


%description
Foomuuri is a firewall generator for nftables based on the concept of zones.
It is suitable for all systems from personal machines to corporate firewalls,
and supports advanced features such as a rich rule language, IPv4/IPv6 rule
splitting, dynamic DNS lookups, a D-Bus API and FirewallD emulation for
NetworkManager's zone support.


%package firewalld
Summary:        FirewallD emulation configuration files for Foomuuri
BuildArch:      noarch
Requires:       %{name} = %{version}


%description firewalld
Foomuuri is a firewall generator for nftables based on the concept of zones.
It is suitable for all systems from personal machines to corporate firewalls,
and supports advanced features such as a rich rule language, IPv4/IPv6 rule
splitting, dynamic DNS lookups, a D-Bus API and FirewallD emulation for
NetworkManager's zone support.

This optional package includes FirewallD emulation configuration files.


%prep
%autosetup -p1


%build


%install
make install PREFIX=%{buildroot}


%post
%systemd_post foomuuri.service foomuuri-dbus.service foomuuri-iplist.timer foomuuri-iplist.service foomuuri-monitor.service foomuuri-resolve.timer foomuuri-resolve.service


%preun
%systemd_preun foomuuri.service foomuuri-dbus.service foomuuri-iplist.timer foomuuri-iplist.service foomuuri-monitor.service foomuuri-resolve.timer foomuuri-resolve.service


%postun
%systemd_postun foomuuri.service foomuuri-iplist.service foomuuri-resolve.service
if [ $1 -ge 1 ]; then
    systemctl reload-or-try-restart foomuuri.service > /dev/null 2>&1 || :
fi
%systemd_postun_with_restart foomuuri-dbus.service foomuuri-monitor.service foomuuri-iplist.timer foomuuri-resolve.timer


%files
%license COPYING
%doc README.md CHANGELOG.md
%doc %{_mandir}/man1/foomuuri.1*
%attr(0750, root, adm) %dir %{_sysconfdir}/foomuuri
%{_sbindir}/foomuuri
%{_sysctldir}/50-foomuuri.conf
%dir %{_datadir}/foomuuri
%{_datadir}/foomuuri/default.services.conf
%{_datadir}/foomuuri/static.nft
%{_unitdir}/foomuuri.service
%{_unitdir}/foomuuri-dbus.service
%{_unitdir}/foomuuri-iplist.service
%{_unitdir}/foomuuri-iplist.timer
%{_unitdir}/foomuuri-monitor.service
%{_unitdir}/foomuuri-resolve.service
%{_unitdir}/foomuuri-resolve.timer
%{_tmpfilesdir}/foomuuri.conf
%attr(0700, root, root) %dir %{_rundir}/foomuuri
%attr(0700, root, root) %dir %{_sharedstatedir}/foomuuri
%{_datadir}/dbus-1/system.d/fi.foobar.Foomuuri1.conf


%files firewalld
%{_datadir}/dbus-1/system.d/fi.foobar.Foomuuri-FirewallD.conf
%{_datadir}/foomuuri/dbus-firewalld.conf


%changelog
* Mon Feb 27 2023 Kim B. Heino <b@bbbs.net> - 0.16-1
- Initial version
