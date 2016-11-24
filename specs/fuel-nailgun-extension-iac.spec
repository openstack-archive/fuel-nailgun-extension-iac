Name:           fuel-nailgun-extension-iac
Version:        9.0.0
Release:        2%{?dist}~mos0
Summary:        Infrastructure as Code extension for Fuel
License:        Apache-2.0
Url:            https://git.openstack.org/cgit/openstack/fuel-nailgun-extension-iac/
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python-devel
BuildRequires:  python-pbr
BuildRequires:  python-setuptools

Requires:       python-pbr
Requires:       GitPython
Requires:       git

%description
Nailgun extension that generates deployment data based on configuration files
published in external git repository

%prep
%setup -q -c -n %{name}-%{version}

%build
export OSLO_PACKAGE_VERSION=%{version} %py2_build

%install
export OSLO_PACKAGE_VERSION=%{version} %py2_install

%files
%license LICENSE
%{python2_sitelib}/fuel_external_git
%{python2_sitelib}/*.egg-info

%changelog
* Fri Nov 18 2016 Dmitrii Nikishov <dnikishov@mirantis.com> - 9.0.0-2.el7~mos0
- Added git to dependencies

* Wed Nov 09 2016 Ivan Udovichenko <iudovichenko@mirantis.com> - 9.0.0-1.el7~mos0
- Rebuild for MOS 9.2
- LP#1640433

* Fri Sep 23 2016 Vladimir Maliaev <vmaliaev@mirantis.com> - 9.0.0
- Initial package.
