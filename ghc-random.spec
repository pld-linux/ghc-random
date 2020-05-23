#
# Conditional build:
%bcond_without	prof	# profiling library
#
%define		pkgname	random
Summary:	A random number library
Summary(pl.UTF-8):	Biblioteka liczb losowych
Name:		ghc-%{pkgname}
Version:	1.1
Release:	1
License:	BSD
Group:		Development/Languages
#Source0Download: http://hackage.haskell.org/package/random
Source0:	http://hackage.haskell.org/package/random-%{version}/%{pkgname}-%{version}.tar.gz
# Source0-md5:	474f10b9389b316e4472b71d20298993
URL:		http://hackage.haskell.org/package/random/
BuildRequires:	ghc >= 6.12.3
BuildRequires:	ghc-base >= 3
BuildRequires:	ghc-base < 5
BuildRequires:	ghc-time
%if %{with prof}
BuildRequires:	ghc-prof >= 6.12.3
BuildRequires:	ghc-base-prof >= 3
BuildRequires:	ghc-base-prof < 5
BuildRequires:	ghc-time-prof
%endif
BuildRequires:	rpmbuild(macros) >= 1.608
%requires_releq	ghc
Requires:	ghc-base >= 3
Requires:	ghc-base < 5
Requires:	ghc-time
Obsoletes:	ghc-random-doc
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# debuginfo is not useful for ghc
%define		_enable_debug_packages	0

# don't compress haddock files
%define		_noautocompressdoc	*.haddock

%description
This package provides a random number library.

%description -l pl.UTF-8
Ten pakiet zawiera bibliotekę liczb losowych.

%package prof
Summary:	Profiling %{pkgname} library for GHC
Summary(pl.UTF-8):	Biblioteka profilująca %{pkgname} dla GHC
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	ghc-base-prof >= 3
Requires:	ghc-base-prof < 5
Requires:	ghc-time-prof

%description prof
Profiling %{pkgname} library for GHC.  Should be installed when
GHC's profiling subsystem is needed.

%description prof -l pl.UTF-8
Biblioteka profilująca %{pkgname} dla GHC. Powinna być zainstalowana
kiedy potrzebujemy systemu profilującego z GHC.

%prep
%setup -q -n %{pkgname}-%{version}

# it relies on ld.bfd specific options
mkdir -p ld-dir
if [ -x /usr/bin/ld.bfd ]; then
	ln -sf /usr/bin/ld.bfd ld-dir/ld
fi

%build
PATH=$(pwd)/ld-dir:$PATH
runhaskell Setup.hs configure -v2 \
	%{?with_prof:--enable-library-profiling} \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--libexecdir=%{_libexecdir} \
	--docdir=%{_docdir}/%{name}-%{version}

runhaskell Setup.hs build
runhaskell Setup.hs haddock --executables

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/package.conf.d

runhaskell Setup.hs copy --destdir=$RPM_BUILD_ROOT

# work around automatic haddock docs installation
rm -rf %{name}-%{version}-doc
cp -a $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version} %{name}-%{version}-doc

runhaskell Setup.hs register \
	--gen-pkg-config=$RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/package.conf.d/%{pkgname}.conf

rm -r $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%ghc_pkg_recache

%postun
%ghc_pkg_recache

%files
%defattr(644,root,root,755)
%doc %{name}-%{version}-doc/*
%{_libdir}/%{ghcdir}/package.conf.d/%{pkgname}.conf
%dir %{_libdir}/%{ghcdir}/%{pkgname}-%{version}
%{_libdir}/%{ghcdir}/%{pkgname}-%{version}/libHSrandom-%{version}-*.a
%exclude %{_libdir}/%{ghcdir}/%{pkgname}-%{version}/libHSrandom-%{version}-*_p.a
%{_libdir}/%{ghcdir}/%{pkgname}-%{version}/libHSrandom-%{version}-*.so
%dir %{_libdir}/%{ghcdir}/%{pkgname}-%{version}/System
%{_libdir}/%{ghcdir}/%{pkgname}-%{version}/System/*.hi
%{_libdir}/%{ghcdir}/%{pkgname}-%{version}/System/*.dyn_hi

%if %{with prof}
%files prof
%defattr(644,root,root,755)
%{_libdir}/%{ghcdir}/%{pkgname}-%{version}/libHSrandom-%{version}-*_p.a
%{_libdir}/%{ghcdir}/%{pkgname}-%{version}/System/*.p_hi
%endif
