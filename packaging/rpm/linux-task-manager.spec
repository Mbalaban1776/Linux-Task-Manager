Name:           linux-task-manager
Version:        0.2.8
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
install -m 644 assets/icons/hicolor/scalable/apps/ltm-icon.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/ltm-icon.svg
install -m 644 assets/icons/hicolor/16x16/apps/ltm-icon.png %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/ltm-icon.png
install -m 644 assets/icons/hicolor/22x22/apps/ltm-icon.png %{buildroot}%{_datadir}/icons/hicolor/22x22/apps/ltm-icon.png
install -m 644 assets/icons/hicolor/32x32/apps/ltm-icon.png %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/ltm-icon.png
install -m 644 assets/icons/hicolor/48x48/apps/ltm-icon.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/ltm-icon.png
install -m 644 assets/icons/hicolor/64x64/apps/ltm-icon.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/ltm-icon.png
install -m 644 assets/icons/hicolor/128x128/apps/ltm-icon.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/ltm-icon.png
install -m 644 assets/icons/hicolor/256x256/apps/ltm-icon.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/ltm-icon.png

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/%{name}.appdata.xml

%files
%license LICENSE
%{_bindir}/%{name}
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/metainfo/%{name}.appdata.xml
%{_datadir}/icons/hicolor/scalable/apps/ltm-icon.svg
%{_datadir}/icons/hicolor/16x16/apps/ltm-icon.png
%{_datadir}/icons/hicolor/22x22/apps/ltm-icon.png
%{_datadir}/icons/hicolor/32x32/apps/ltm-icon.png
%{_datadir}/icons/hicolor/48x48/apps/ltm-icon.png
%{_datadir}/icons/hicolor/64x64/apps/ltm-icon.png
%{_datadir}/icons/hicolor/128x128/apps/ltm-icon.png
%{_datadir}/icons/hicolor/256x256/apps/ltm-icon.png

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
* Wed Jun 12 2024 Mustafa Balaban <mustafabalaban46@gmail.com> - 0.2.8-1
- Added screenshot for software center.
- Fixed icon display issues in software center.

* Wed May 08 2025 Mustafa Balaban <mustafabalaban46@gmail.com> - 0.2.7-1
- Corrected CPU usage to be system-wide instead of per-core.
- Corrected memory usage to report Unique Set Size (USS) for accuracy.
- Aligned resource graphs with the new, more accurate data calculations.
- Fixed a crash related to inconsistent variable use in the process view.

* Wed May 08 2025 Mustafa Balaban <mustafabalaban46@gmail.com> - 0.2.6-1
- Implemented a comprehensive memory monitoring view similar to Windows.
- Added a memory usage history graph and a composition bar.
- Included detailed memory statistics like "In use," "Available," and "Cached."
- Fixed a bug causing crashes when processes terminated during data collection.
- Added percentage labels to the CPU usage graph for better readability.

* Tue May 07 2025 Mustafa Balaban <mustafabalaban46@gmail.com> - 0.2.5-1
- Added process search functionality with a new search bar.
- Implemented process icon display for better visual identification.
- Redesigned header to integrate search and tab switching for a cleaner UI.
- Improved icon loading logic with better caching and more accurate mappings.
- Fixed a critical bug preventing sorting of processes by CPU, PID, and Memory.
- Polished UI details, including button colors and search bar placeholder behavior.

* Mon May 06 2025 Mustafa Balaban <mustafabalaban46@gmail.com> - 0.2.4-1
- Use absolute path for icon to work around caching issues

* Mon May 06 2025 Mustafa Balaban <mustafabalaban46@gmail.com> - 0.2.3-1
- Renamed icon files to bypass desktop caching issues

* Sun May 05 2025 Mustafa Balaban <mustafabalaban46@gmail.com> - 0.2.2-1
- Force icon update attempt

* Sun May 05 2025 Mustafa Balaban <mustafabalaban46@gmail.com> - 0.2.1-1
- Updated application icon

* Sun May 04 2025 Mustafa Balaban <mustafabalaban46@gmail.com> - 0.2.0-1
- Added dark mode toggle
- Added icons to navigation tabs
- Made End Process button red with white text
- Improved process list with proportional columns
- Fixed CPU usage display
- Enhanced UI responsiveness

* Sat May 03 2025 Mustafa Balaban <mustafabalaban46@gmail.com> - 0.1.0-1
- Initial package