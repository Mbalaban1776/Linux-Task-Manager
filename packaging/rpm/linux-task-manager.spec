Name:           linux-task-manager
Version:        0.1.0
Release:        1%{?dist}
Summary:        A system task manager for Linux

License:        MIT
URL:            https://github.com/Mbalaban1776/Linux-Task-Manager
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
Requires:       python3
Requires:       python3-psutil
Requires:       python3-gobject
Requires:       gtk3

%description
Linux Task Manager allows you to monitor system processes, 
CPU usage, memory usage, network activity, disk usage and file systems.
It provides a user-friendly interface to view and manage running processes.

%prep
%autosetup

%build
# Nothing to build for Python application

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/metainfo
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/16x16/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/22x22/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/32x32/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/48x48/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/64x64/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/128x128/apps
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps

# Install the main script
install -m 755 src/linux-task-manager %{buildroot}%{_bindir}/%{name}

# Install the Python package
cp -r src/* %{buildroot}%{_datadir}/%{name}/

# Install the desktop file
desktop-file-install --dir=%{buildroot}%{_datadir}/applications packaging/linux-task-manager.desktop

# Install AppStream metadata
install -m 644 packaging/linux-task-manager.appdata.xml %{buildroot}%{_datadir}/metainfo/%{name}.appdata.xml

# Install icons
install -m 644 assets/icons/hicolor/scalable/apps/linux-task-manager.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
install -m 644 assets/icons/hicolor/16x16/apps/linux-task-manager.png %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
install -m 644 assets/icons/hicolor/22x22/apps/linux-task-manager.png %{buildroot}%{_datadir}/icons/hicolor/22x22/apps/%{name}.png
install -m 644 assets/icons/hicolor/32x32/apps/linux-task-manager.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
install -m 644 assets/icons/hicolor/48x48/apps/linux-task-manager.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
install -m 644 assets/icons/hicolor/64x64/apps/linux-task-manager.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/%{name}.png
install -m 644 assets/icons/hicolor/128x128/apps/linux-task-manager.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{name}.png
install -m 644 assets/icons/hicolor/256x256/apps/linux-task-manager.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/%{name}.png

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/%{name}.appdata.xml

%files
%license LICENSE
%{_bindir}/%{name}
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/metainfo/%{name}.appdata.xml
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
%{_datadir}/icons/hicolor/22x22/apps/%{name}.png
%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
%{_datadir}/icons/hicolor/64x64/apps/%{name}.png
%{_datadir}/icons/hicolor/128x128/apps/%{name}.png
%{_datadir}/icons/hicolor/256x256/apps/%{name}.png

%post
/usr/bin/update-desktop-database &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
/usr/bin/update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%changelog
* Sat May 03 2025 Mustafa Balaban <mustafabalaban46@gmail.com> - 0.1.0-1
- Initial package