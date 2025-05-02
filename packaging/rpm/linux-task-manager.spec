Name:           linux-task-manager
Version:        0.1.0
Release:        1%{?dist}
Summary:        A system task manager for Linux

License:        MIT
URL:            https://github.com/mustafabalaban/Linux-Task-Manager
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
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

# Install the main script
install -m 755 src/linux-task-manager %{buildroot}%{_bindir}/%{name}

# Install the Python package
cp -r src/* %{buildroot}%{_datadir}/%{name}/

# Install the desktop file
install -m 644 packaging/linux-task-manager.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop

%files
%license LICENSE
%{_bindir}/%{name}
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop

%changelog
* Thu May 01 2025 Mustafa Balaban <your.email@example.com> - 0.1.0-1
- Initial package