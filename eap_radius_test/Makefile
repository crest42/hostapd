ifndef CC
CC=gcc
endif

ifndef CFLAGS
CFLAGS = -MMD -O2 -Wall -g
endif

ifdef LIBS
# If LIBS is set with some global build system defaults, clone those for
# LIBS_c and LIBS_p to cover wpa_passphrase and wpa_cli as well.
ifndef LIBS_c
LIBS_c := $(LIBS)
endif
ifndef LIBS_p
LIBS_p := $(LIBS)
endif
endif

export LIBDIR ?= /usr/local/lib/
export INCDIR ?= /usr/local/include/
export BINDIR ?= /usr/local/sbin/
PKG_CONFIG ?= pkg-config

CFLAGS += $(EXTRA_CFLAGS)
CFLAGS += -I$(abspath ../src)
CFLAGS += -I$(abspath ../src/utils)

-include .config

ifndef CONFIG_NO_GITVER
# Add VERSION_STR postfix for builds from a git repository
ifeq ($(wildcard ../.git),../.git)
GITVER := $(shell git describe --dirty=+)
ifneq ($(GITVER),)
CFLAGS += -DGIT_VERSION_STR_POSTFIX=\"-$(GITVER)\"
endif
endif
endif

ifdef CONFIG_TESTING_OPTIONS
CFLAGS += -DCONFIG_TESTING_OPTIONS
CONFIG_WPS_TESTING=y
CONFIG_TDLS_TESTING=y
endif


ifndef CONFIG_NO_WPA_PASSPHRASE
BINALL += wpa_passphrase
endif

ALL = $(BINALL)
ALL += systemd/wpa_supplicant.service
ALL += systemd/wpa_supplicant@.service
ALL += systemd/wpa_supplicant-nl80211@.service
ALL += systemd/wpa_supplicant-wired@.service
ALL += dbus/fi.w1.wpa_supplicant1.service
ifdef CONFIG_BUILD_WPA_CLIENT_SO
ALL += libwpa_client.so
endif


all: verify_config $(ALL) dynamic_eap_methods

verify_config:
	@if [ ! -r .config ]; then \
		echo 'Building wpa_supplicant requires a configuration file'; \
		echo '(.config). See README for more instructions. You can'; \
		echo 'run "cp defconfig .config" to create an example'; \
		echo 'configuration.'; \
		exit 1; \
	fi

mkconfig:
	@if [ -f .config ]; then \
		echo '.config exists - did not replace it'; \
		exit 1; \
	fi
	echo CONFIG_DRIVER_HOSTAP=y >> .config
	echo CONFIG_DRIVER_WEXT=y >> .config

$(DESTDIR)$(BINDIR)/%: %
	install -D $(<) $(@)

install: $(addprefix $(DESTDIR)$(BINDIR)/,$(BINALL))
	$(MAKE) -C ../src install
ifdef CONFIG_BUILD_WPA_CLIENT_SO
	install -m 0644 -D libwpa_client.so $(DESTDIR)/$(LIBDIR)/libwpa_client.so
	install -m 0644 -D ../src/common/wpa_ctrl.h $(DESTDIR)/$(INCDIR)/wpa_ctrl.h
endif

ifdef CONFIG_FIPS
CONFIG_NO_RANDOM_POOL=
CONFIG_OPENSSL_CMAC=y
endif

OBJS = config.o
OBJS += eap_register.o
OBJS += ../src/utils/common.o
OBJS += ../src/utils/wpa_debug.o
OBJS += ../src/utils/wpabuf.o
OBJS += ../src/utils/bitfield.o
OBJS += ../src/utils/ip_addr.o
OBJS += ../src/utils/crc32.o
OBJS_p = wpa_passphrase.o
OBJS_p += ../src/utils/common.o
OBJS_p += ../src/utils/wpa_debug.o
OBJS_p += ../src/utils/wpabuf.o
OBJS_c = wpa_cli.o ../src/common/wpa_ctrl.o
OBJS_c += ../src/utils/wpa_debug.o
OBJS_c += ../src/utils/common.o
OBJS_c += ../src/common/cli.o

ifndef CONFIG_OS
ifdef CONFIG_NATIVE_WINDOWS
CONFIG_OS=win32
else
CONFIG_OS=unix
endif
endif

ifeq ($(CONFIG_OS), internal)
CFLAGS += -DOS_NO_C_LIB_DEFINES
endif

OBJS += ../src/utils/os_$(CONFIG_OS).o
OBJS_p += ../src/utils/os_$(CONFIG_OS).o
OBJS_c += ../src/utils/os_$(CONFIG_OS).o

ifdef CONFIG_WPA_TRACE
CFLAGS += -DWPA_TRACE
OBJS += ../src/utils/trace.o
OBJS_p += ../src/utils/trace.o
OBJS_c += ../src/utils/trace.o
OBJS_priv += ../src/utils/trace.o
LIBCTRL += ../src/utils/trace.o
LIBCTRLSO += ../src/utils/trace.c
LDFLAGS += -rdynamic
CFLAGS += -funwind-tables
ifdef CONFIG_WPA_TRACE_BFD
CFLAGS += -DPACKAGE="wpa_supplicant" -DWPA_TRACE_BFD
LIBS += -lbfd -ldl -liberty -lz
LIBS_p += -lbfd -ldl -liberty -lz
LIBS_c += -lbfd -ldl -liberty -lz
endif
endif

ifndef CONFIG_ELOOP
CONFIG_ELOOP=eloop
endif
OBJS += ../src/utils/$(CONFIG_ELOOP).o
OBJS_c += ../src/utils/$(CONFIG_ELOOP).o

ifndef CONFIG_OSX
ifeq ($(CONFIG_ELOOP), eloop)
# Using glibc < 2.17 requires -lrt for clock_gettime()
# OS X has an alternate implementation
LIBS += -lrt
LIBS_c += -lrt
LIBS_p += -lrt
endif
endif

ifdef CONFIG_ELOOP_POLL
CFLAGS += -DCONFIG_ELOOP_POLL
endif

ifdef CONFIG_ELOOP_EPOLL
CFLAGS += -DCONFIG_ELOOP_EPOLL
endif

ifdef CONFIG_ELOOP_KQUEUE
CFLAGS += -DCONFIG_ELOOP_KQUEUE
endif

ifdef CONFIG_EAPOL_TEST
CFLAGS += -Werror -DEAPOL_TEST
endif

ifdef CONFIG_CODE_COVERAGE
CFLAGS += -O0 -fprofile-arcs -ftest-coverage
LIBS += -lgcov
LIBS_c += -lgcov
LIBS_p += -lgcov
endif

ifdef CONFIG_HT_OVERRIDES
CFLAGS += -DCONFIG_HT_OVERRIDES
endif

ifdef CONFIG_VHT_OVERRIDES
CFLAGS += -DCONFIG_VHT_OVERRIDES
endif

ifdef CONFIG_HE_OVERRIDES
CFLAGS += -DCONFIG_HE_OVERRIDES
endif

ifndef CONFIG_BACKEND
CONFIG_BACKEND=file
endif

ifeq ($(CONFIG_BACKEND), file)
OBJS += config_file.o
ifndef CONFIG_NO_CONFIG_BLOBS
NEED_BASE64=y
endif
CFLAGS += -DCONFIG_BACKEND_FILE
endif

ifeq ($(CONFIG_BACKEND), winreg)
OBJS += config_winreg.o
endif

ifeq ($(CONFIG_BACKEND), none)
OBJS += config_none.o
endif

ifdef CONFIG_NO_CONFIG_WRITE
CFLAGS += -DCONFIG_NO_CONFIG_WRITE
endif

ifdef CONFIG_NO_CONFIG_BLOBS
CFLAGS += -DCONFIG_NO_CONFIG_BLOBS
endif

ifdef CONFIG_NO_SCAN_PROCESSING
CFLAGS += -DCONFIG_NO_SCAN_PROCESSING
endif

ifdef CONFIG_SUITEB
CFLAGS += -DCONFIG_SUITEB
endif

ifdef CONFIG_SUITEB192
CFLAGS += -DCONFIG_SUITEB192
NEED_SHA384=y
endif

ifdef CONFIG_OCV
CFLAGS += -DCONFIG_OCV
OBJS += ../src/common/ocv.o
endif

ifdef CONFIG_IEEE80211R
CFLAGS += -DCONFIG_IEEE80211R
OBJS += ../src/rsn_supp/wpa_ft.o
endif

ifdef CONFIG_MESH
NEED_80211_COMMON=y
NEED_AES_SIV=y
CONFIG_SAE=y
CONFIG_AP=y
CFLAGS += -DCONFIG_MESH
OBJS += mesh.o
OBJS += mesh_mpm.o
OBJS += mesh_rsn.o
endif


ifdef CONFIG_OWE
CFLAGS += -DCONFIG_OWE
NEED_ECC=y
NEED_HMAC_SHA256_KDF=y
NEED_HMAC_SHA384_KDF=y
NEED_HMAC_SHA512_KDF=y
NEED_SHA384=y
NEED_SHA512=y
endif

ifdef CONFIG_FILS
CFLAGS += -DCONFIG_FILS
NEED_SHA384=y
NEED_AES_SIV=y
ifdef CONFIG_FILS_SK_PFS
CFLAGS += -DCONFIG_FILS_SK_PFS
NEED_ECC=y
endif
endif

ifdef CONFIG_MBO
CONFIG_WNM=y
endif

ifdef CONFIG_WNM
CFLAGS += -DCONFIG_WNM
OBJS += wnm_sta.o
endif

ifdef CONFIG_TDLS
CFLAGS += -DCONFIG_TDLS
OBJS += ../src/rsn_supp/tdls.o
endif

ifdef CONFIG_TDLS_TESTING
CFLAGS += -DCONFIG_TDLS_TESTING
endif

ifdef CONFIG_PMKSA_CACHE_EXTERNAL
CFLAGS += -DCONFIG_PMKSA_CACHE_EXTERNAL
endif

ifndef CONFIG_NO_WPA
OBJS += ../src/rsn_supp/wpa.o
OBJS += ../src/rsn_supp/preauth.o
OBJS += ../src/rsn_supp/pmksa_cache.o
OBJS += ../src/rsn_supp/wpa_ie.o
OBJS += ../src/common/wpa_common.o
NEED_AES=y
NEED_SHA1=y
NEED_MD5=y
NEED_RC4=y
else
CFLAGS += -DCONFIG_NO_WPA
ifeq ($(CONFIG_TLS), internal)
NEED_SHA1=y
NEED_MD5=y
endif
endif

ifdef CONFIG_MATCH_IFACE
CFLAGS += -DCONFIG_MATCH_IFACE
endif

include ../src/drivers/drivers.mak
ifdef CONFIG_AP
OBJS_d += $(DRV_BOTH_OBJS)
CFLAGS += $(DRV_BOTH_CFLAGS)
LDFLAGS += $(DRV_BOTH_LDFLAGS)
LIBS += $(DRV_BOTH_LIBS)
else
NEED_AP_MLME=
OBJS_d += $(DRV_WPA_OBJS)
CFLAGS += $(DRV_WPA_CFLAGS)
LDFLAGS += $(DRV_WPA_LDFLAGS)
LIBS += $(DRV_WPA_LIBS)
endif

ifndef CONFIG_L2_PACKET
CONFIG_L2_PACKET=linux
endif

OBJS_l2 += ../src/l2_packet/l2_packet_$(CONFIG_L2_PACKET).o

ifeq ($(CONFIG_L2_PACKET), pcap)
ifdef CONFIG_WINPCAP
CFLAGS += -DCONFIG_WINPCAP
LIBS += -lwpcap -lpacket
LIBS_w += -lwpcap
else
LIBS += -ldnet -lpcap
endif
endif

ifeq ($(CONFIG_L2_PACKET), winpcap)
LIBS += -lwpcap -lpacket
LIBS_w += -lwpcap
endif

ifeq ($(CONFIG_L2_PACKET), freebsd)
LIBS += -lpcap
endif

ifdef CONFIG_ERP
CFLAGS += -DCONFIG_ERP
NEED_HMAC_SHA256_KDF=y
endif

ifdef CONFIG_EAP_TLS
# EAP-TLS
ifeq ($(CONFIG_EAP_TLS), dyn)
CFLAGS += -DEAP_TLS_DYNAMIC
EAPDYN += ../src/eap_peer/eap_tls.so
else
CFLAGS += -DEAP_TLS
OBJS += ../src/eap_peer/eap_tls.o
endif
TLS_FUNCS=y
CONFIG_IEEE8021X_EAPOL=y
endif

ifdef CONFIG_EAP_UNAUTH_TLS
# EAP-UNAUTH-TLS
CFLAGS += -DEAP_UNAUTH_TLS
ifndef CONFIG_EAP_TLS
OBJS += ../src/eap_peer/eap_tls.o
TLS_FUNCS=y
endif
CONFIG_IEEE8021X_EAPOL=y
endif

ifdef CONFIG_EAP_PEAP
# EAP-PEAP
ifeq ($(CONFIG_EAP_PEAP), dyn)
CFLAGS += -DEAP_PEAP_DYNAMIC
EAPDYN += ../src/eap_peer/eap_peap.so
else
CFLAGS += -DEAP_PEAP
OBJS += ../src/eap_peer/eap_peap.o
OBJS += ../src/eap_common/eap_peap_common.o
endif
TLS_FUNCS=y
CONFIG_IEEE8021X_EAPOL=y
endif

ifdef CONFIG_EAP_PSK
# EAP-PSK
ifeq ($(CONFIG_EAP_PSK), dyn)
CFLAGS += -DEAP_PSK_DYNAMIC
EAPDYN += ../src/eap_peer/eap_psk.so
else
CFLAGS += -DEAP_PSK
OBJS += ../src/eap_peer/eap_psk.o ../src/eap_common/eap_psk_common.o
endif
CONFIG_IEEE8021X_EAPOL=y
NEED_AES=y
NEED_AES_ENCBLOCK=y
NEED_AES_EAX=y
endif

ifdef CONFIG_EAP_PROXY
CFLAGS += -DCONFIG_EAP_PROXY
OBJS += ../src/eap_peer/eap_proxy_$(CONFIG_EAP_PROXY).o
include eap_proxy_$(CONFIG_EAP_PROXY).mak
CONFIG_IEEE8021X_EAPOL=y
endif

ifdef CONFIG_EAP_FAST
# EAP-FAST
ifeq ($(CONFIG_EAP_FAST), dyn)
CFLAGS += -DEAP_FAST_DYNAMIC
EAPDYN += ../src/eap_peer/eap_fast.so
EAPDYN += ../src/eap_common/eap_fast_common.o
else
CFLAGS += -DEAP_FAST
OBJS += ../src/eap_peer/eap_fast.o ../src/eap_peer/eap_fast_pac.o
OBJS += ../src/eap_common/eap_fast_common.o
endif
TLS_FUNCS=y
CONFIG_IEEE8021X_EAPOL=y
NEED_T_PRF=y
endif

ifdef CONFIG_EAP_TEAP
# EAP-TEAP
ifeq ($(CONFIG_EAP_TEAP), dyn)
CFLAGS += -DEAP_TEAP_DYNAMIC
EAPDYN += ../src/eap_peer/eap_teap.so
EAPDYN += ../src/eap_common/eap_teap_common.o
else
CFLAGS += -DEAP_TEAP
OBJS += ../src/eap_peer/eap_teap.o ../src/eap_peer/eap_teap_pac.o
OBJS += ../src/eap_common/eap_teap_common.o
endif
TLS_FUNCS=y
CONFIG_IEEE8021X_EAPOL=y
NEED_T_PRF=y
NEED_SHA384=y
NEED_TLS_PRF_SHA256=y
NEED_TLS_PRF_SHA384=y
endif

ifdef CONFIG_EAP_PAX
# EAP-PAX
ifeq ($(CONFIG_EAP_PAX), dyn)
CFLAGS += -DEAP_PAX_DYNAMIC
EAPDYN += ../src/eap_peer/eap_pax.so
else
CFLAGS += -DEAP_PAX
OBJS += ../src/eap_peer/eap_pax.o ../src/eap_common/eap_pax_common.o
endif
CONFIG_IEEE8021X_EAPOL=y
endif

ifdef CONFIG_EAP_SAKE
# EAP-SAKE
ifeq ($(CONFIG_EAP_SAKE), dyn)
CFLAGS += -DEAP_SAKE_DYNAMIC
EAPDYN += ../src/eap_peer/eap_sake.so
else
CFLAGS += -DEAP_SAKE
OBJS += ../src/eap_peer/eap_sake.o ../src/eap_common/eap_sake_common.o
endif
CONFIG_IEEE8021X_EAPOL=y
endif

ifdef CONFIG_EAP_GPSK
# EAP-GPSK
ifeq ($(CONFIG_EAP_GPSK), dyn)
CFLAGS += -DEAP_GPSK_DYNAMIC
EAPDYN += ../src/eap_peer/eap_gpsk.so
else
CFLAGS += -DEAP_GPSK
OBJS += ../src/eap_peer/eap_gpsk.o ../src/eap_common/eap_gpsk_common.o
endif
CONFIG_IEEE8021X_EAPOL=y
ifdef CONFIG_EAP_GPSK_SHA256
CFLAGS += -DEAP_GPSK_SHA256
endif
endif

ifdef CONFIG_EAP_VENDOR_TEST
ifeq ($(CONFIG_EAP_VENDOR_TEST), dyn)
CFLAGS += -DEAP_VENDOR_TEST_DYNAMIC
EAPDYN += ../src/eap_peer/eap_vendor_test.so
else
CFLAGS += -DEAP_VENDOR_TEST
OBJS += ../src/eap_peer/eap_vendor_test.o
endif
CONFIG_IEEE8021X_EAPOL=y
endif


ifdef CONFIG_IEEE8021X_EAPOL
# IEEE 802.1X/EAPOL state machines (e.g., for RADIUS authentication)
CFLAGS += -DIEEE8021X_EAPOL
OBJS += ../src/eapol_supp/eapol_supp_sm.o
OBJS += ../src/eap_peer/eap.o ../src/eap_peer/eap_methods.o
NEED_EAP_COMMON=y
ifdef CONFIG_DYNAMIC_EAP_METHODS
CFLAGS += -DCONFIG_DYNAMIC_EAP_METHODS
LIBS += -ldl -rdynamic
endif
endif

ifdef TLS_FUNCS
NEED_DES=y
# Shared TLS functions (needed for EAP_TLS, EAP_PEAP, EAP_TTLS, EAP_FAST, and
# EAP_TEAP)
OBJS += ../src/eap_peer/eap_tls_common.o
ifndef CONFIG_FIPS
NEED_TLS_PRF=y
NEED_SHA1=y
NEED_MD5=y
endif
endif

ifndef CONFIG_TLS
CONFIG_TLS=openssl
endif

ifdef CONFIG_TLSV11
CFLAGS += -DCONFIG_TLSV11
endif

ifdef CONFIG_TLSV12
CFLAGS += -DCONFIG_TLSV12
endif

ifeq ($(CONFIG_TLS), openssl)
ifdef TLS_FUNCS
CFLAGS += -DEAP_TLS_OPENSSL
OBJS += ../src/crypto/tls_openssl.o
OBJS += ../src/crypto/tls_openssl_ocsp.o
LIBS += -lssl
endif
OBJS += ../src/crypto/crypto_openssl.o
OBJS_p += ../src/crypto/crypto_openssl.o
OBJS_priv += ../src/crypto/crypto_openssl.o
ifdef NEED_FIPS186_2_PRF
OBJS += ../src/crypto/fips_prf_openssl.o
endif
NEED_TLS_PRF_SHA256=y
LIBS += -lcrypto
LIBS_p += -lcrypto
ifdef CONFIG_TLS_ADD_DL
LIBS += -ldl
LIBS_p += -ldl
endif
ifndef CONFIG_TLS_DEFAULT_CIPHERS
CONFIG_TLS_DEFAULT_CIPHERS = "DEFAULT:!EXP:!LOW"
endif
CFLAGS += -DTLS_DEFAULT_CIPHERS=\"$(CONFIG_TLS_DEFAULT_CIPHERS)\"
endif

AESOBJS = # none so far (see below)
ifdef CONFIG_INTERNAL_AES
AESOBJS += ../src/crypto/aes-internal.o ../src/crypto/aes-internal-dec.o
endif

ifneq ($(CONFIG_TLS), openssl)
ifneq ($(CONFIG_TLS), wolfssl)
NEED_INTERNAL_AES_WRAP=y
endif
endif
ifdef CONFIG_OPENSSL_INTERNAL_AES_WRAP
# Seems to be needed at least with BoringSSL
NEED_INTERNAL_AES_WRAP=y
CFLAGS += -DCONFIG_OPENSSL_INTERNAL_AES_WRAP
endif
ifdef CONFIG_FIPS
# Have to use internal AES key wrap routines to use OpenSSL EVP since the
# OpenSSL AES_wrap_key()/AES_unwrap_key() API is not available in FIPS mode.
NEED_INTERNAL_AES_WRAP=y
endif

ifdef NEED_INTERNAL_AES_WRAP
ifneq ($(CONFIG_TLS), linux)
AESOBJS += ../src/crypto/aes-unwrap.o
endif
endif
ifdef NEED_AES_EAX
AESOBJS += ../src/crypto/aes-eax.o
NEED_AES_CTR=y
endif
ifdef NEED_AES_SIV
AESOBJS += ../src/crypto/aes-siv.o
NEED_AES_CTR=y
endif
ifdef NEED_AES_CTR
AESOBJS += ../src/crypto/aes-ctr.o
endif
ifdef NEED_AES_ENCBLOCK
AESOBJS += ../src/crypto/aes-encblock.o
endif
NEED_AES_ENC=y
ifdef CONFIG_OPENSSL_CMAC
CFLAGS += -DCONFIG_OPENSSL_CMAC
else
ifneq ($(CONFIG_TLS), linux)
ifneq ($(CONFIG_TLS), wolfssl)
AESOBJS += ../src/crypto/aes-omac1.o
endif
endif
endif
ifdef NEED_AES_WRAP
NEED_AES_ENC=y
ifdef NEED_INTERNAL_AES_WRAP
AESOBJS += ../src/crypto/aes-wrap.o
endif
endif
ifdef NEED_AES_CBC
NEED_AES_ENC=y
ifneq ($(CONFIG_TLS), openssl)
ifneq ($(CONFIG_TLS), linux)
ifneq ($(CONFIG_TLS), wolfssl)
AESOBJS += ../src/crypto/aes-cbc.o
endif
endif
endif
endif
ifdef NEED_AES_ENC
ifdef CONFIG_INTERNAL_AES
AESOBJS += ../src/crypto/aes-internal-enc.o
endif
endif
ifdef NEED_AES
OBJS += $(AESOBJS)
endif

ifdef NEED_SHA1
ifneq ($(CONFIG_TLS), openssl)
ifneq ($(CONFIG_TLS), linux)
ifneq ($(CONFIG_TLS), gnutls)
ifneq ($(CONFIG_TLS), wolfssl)
SHA1OBJS += ../src/crypto/sha1.o
endif
endif
endif
endif
SHA1OBJS += ../src/crypto/sha1-prf.o
ifdef CONFIG_INTERNAL_SHA1
SHA1OBJS += ../src/crypto/sha1-internal.o
ifdef NEED_FIPS186_2_PRF
SHA1OBJS += ../src/crypto/fips_prf_internal.o
endif
endif
ifdef CONFIG_NO_WPA_PASSPHRASE
CFLAGS += -DCONFIG_NO_PBKDF2
else
ifneq ($(CONFIG_TLS), openssl)
ifneq ($(CONFIG_TLS), wolfssl)
SHA1OBJS += ../src/crypto/sha1-pbkdf2.o
endif
endif
endif
ifdef NEED_T_PRF
SHA1OBJS += ../src/crypto/sha1-tprf.o
endif
ifdef NEED_TLS_PRF
SHA1OBJS += ../src/crypto/sha1-tlsprf.o
endif
endif

ifndef CONFIG_FIPS
ifneq ($(CONFIG_TLS), openssl)
ifneq ($(CONFIG_TLS), linux)
ifneq ($(CONFIG_TLS), gnutls)
ifneq ($(CONFIG_TLS), wolfssl)
MD5OBJS += ../src/crypto/md5.o
endif
endif
endif
endif
endif
ifdef NEED_MD5
ifdef CONFIG_INTERNAL_MD5
MD5OBJS += ../src/crypto/md5-internal.o
endif
OBJS += $(MD5OBJS)
OBJS_p += $(MD5OBJS)
OBJS_priv += $(MD5OBJS)
endif

ifdef NEED_MD4
ifdef CONFIG_INTERNAL_MD4
OBJS += ../src/crypto/md4-internal.o
endif
endif

DESOBJS = # none needed when not internal
ifdef NEED_DES
ifndef CONFIG_FIPS
CFLAGS += -DCONFIG_DES
endif
ifdef CONFIG_INTERNAL_DES
DESOBJS += ../src/crypto/des-internal.o
endif
endif

ifdef CONFIG_NO_RC4
CFLAGS += -DCONFIG_NO_RC4
endif

ifdef NEED_RC4
ifdef CONFIG_INTERNAL_RC4
ifndef CONFIG_NO_RC4
OBJS += ../src/crypto/rc4.o
endif
endif
endif

SHA256OBJS = # none by default
CFLAGS += -DCONFIG_SHA256
ifneq ($(CONFIG_TLS), openssl)
ifneq ($(CONFIG_TLS), linux)
ifneq ($(CONFIG_TLS), gnutls)
ifneq ($(CONFIG_TLS), wolfssl)
SHA256OBJS += ../src/crypto/sha256.o
endif
endif
endif
endif
SHA256OBJS += ../src/crypto/sha256-prf.o
ifdef CONFIG_INTERNAL_SHA256
SHA256OBJS += ../src/crypto/sha256-internal.o
endif
ifdef CONFIG_INTERNAL_SHA384
CFLAGS += -DCONFIG_INTERNAL_SHA384
SHA256OBJS += ../src/crypto/sha384-internal.o
endif
ifdef CONFIG_INTERNAL_SHA512
CFLAGS += -DCONFIG_INTERNAL_SHA512
SHA256OBJS += ../src/crypto/sha512-internal.o
endif
ifdef NEED_TLS_PRF_SHA256
SHA256OBJS += ../src/crypto/sha256-tlsprf.o
endif
ifdef NEED_TLS_PRF_SHA384
SHA256OBJS += ../src/crypto/sha384-tlsprf.o
endif
ifdef NEED_HMAC_SHA256_KDF
CFLAGS += -DCONFIG_HMAC_SHA256_KDF
OBJS += ../src/crypto/sha256-kdf.o
endif
ifdef NEED_HMAC_SHA384_KDF
CFLAGS += -DCONFIG_HMAC_SHA384_KDF
OBJS += ../src/crypto/sha384-kdf.o
endif
ifdef NEED_HMAC_SHA512_KDF
CFLAGS += -DCONFIG_HMAC_SHA512_KDF
OBJS += ../src/crypto/sha512-kdf.o
endif
OBJS += $(SHA256OBJS)
ifdef NEED_SHA384
ifneq ($(CONFIG_TLS), openssl)
ifneq ($(CONFIG_TLS), linux)
ifneq ($(CONFIG_TLS), gnutls)
ifneq ($(CONFIG_TLS), wolfssl)
OBJS += ../src/crypto/sha384.o
endif
endif
endif
endif
CFLAGS += -DCONFIG_SHA384
OBJS += ../src/crypto/sha384-prf.o
endif
ifdef NEED_SHA512
ifneq ($(CONFIG_TLS), openssl)
ifneq ($(CONFIG_TLS), linux)
ifneq ($(CONFIG_TLS), gnutls)
ifneq ($(CONFIG_TLS), wolfssl)
OBJS += ../src/crypto/sha512.o
endif
endif
endif
endif
CFLAGS += -DCONFIG_SHA512
OBJS += ../src/crypto/sha512-prf.o
endif

ifdef NEED_ASN1
OBJS += ../src/tls/asn1.o
endif

ifdef NEED_DH_GROUPS
OBJS += ../src/crypto/dh_groups.o
endif
ifdef NEED_DH_GROUPS_ALL
CFLAGS += -DALL_DH_GROUPS
endif
ifdef CONFIG_INTERNAL_DH_GROUP5
ifdef NEED_DH_GROUPS
OBJS += ../src/crypto/dh_group5.o
endif
endif

ifdef NEED_ECC
CFLAGS += -DCONFIG_ECC
endif

ifdef CONFIG_NO_RANDOM_POOL
CFLAGS += -DCONFIG_NO_RANDOM_POOL
else
ifdef CONFIG_GETRANDOM
CFLAGS += -DCONFIG_GETRANDOM
endif
OBJS += ../src/crypto/random.o
endif

ifdef CONFIG_CTRL_IFACE
ifeq ($(CONFIG_CTRL_IFACE), y)
ifdef CONFIG_NATIVE_WINDOWS
CONFIG_CTRL_IFACE=named_pipe
else
CONFIG_CTRL_IFACE=unix
endif
endif
CFLAGS += -DCONFIG_CTRL_IFACE
ifeq ($(CONFIG_CTRL_IFACE), unix)
CFLAGS += -DCONFIG_CTRL_IFACE_UNIX
OBJS += ../src/common/ctrl_iface_common.o
endif
ifeq ($(CONFIG_CTRL_IFACE), udp)
CFLAGS += -DCONFIG_CTRL_IFACE_UDP
endif
ifeq ($(CONFIG_CTRL_IFACE), udp6)
CONFIG_CTRL_IFACE=udp
CFLAGS += -DCONFIG_CTRL_IFACE_UDP
CFLAGS += -DCONFIG_CTRL_IFACE_UDP_IPV6
endif
ifeq ($(CONFIG_CTRL_IFACE), named_pipe)
CFLAGS += -DCONFIG_CTRL_IFACE_NAMED_PIPE
endif
ifeq ($(CONFIG_CTRL_IFACE), udp-remote)
CONFIG_CTRL_IFACE=udp
CFLAGS += -DCONFIG_CTRL_IFACE_UDP
CFLAGS += -DCONFIG_CTRL_IFACE_UDP_REMOTE
endif
ifeq ($(CONFIG_CTRL_IFACE), udp6-remote)
CONFIG_CTRL_IFACE=udp
CFLAGS += -DCONFIG_CTRL_IFACE_UDP
CFLAGS += -DCONFIG_CTRL_IFACE_UDP_REMOTE
CFLAGS += -DCONFIG_CTRL_IFACE_UDP_IPV6
endif
OBJS += ctrl_iface.o ctrl_iface_$(CONFIG_CTRL_IFACE).o
endif

ifdef CONFIG_READLINE
OBJS_c += ../src/utils/edit_readline.o
LIBS_c += -lreadline -lncurses
else
ifdef CONFIG_WPA_CLI_EDIT
OBJS_c += ../src/utils/edit.o
else
OBJS_c += ../src/utils/edit_simple.o
endif
endif

ifdef CONFIG_NATIVE_WINDOWS
CFLAGS += -DCONFIG_NATIVE_WINDOWS
LIBS += -lws2_32 -lgdi32 -lcrypt32
LIBS_c += -lws2_32
LIBS_p += -lws2_32 -lgdi32
ifeq ($(CONFIG_CRYPTO), cryptoapi)
LIBS_p += -lcrypt32
endif
endif

ifdef CONFIG_NO_STDOUT_DEBUG
CFLAGS += -DCONFIG_NO_STDOUT_DEBUG
ifndef CONFIG_CTRL_IFACE
CFLAGS += -DCONFIG_NO_WPA_MSG
endif
endif

ifdef CONFIG_IPV6
# for eapol_test only
CFLAGS += -DCONFIG_IPV6
endif

ifdef CONFIG_NO_LINUX_PACKET_SOCKET_WAR
CFLAGS += -DCONFIG_NO_LINUX_PACKET_SOCKET_WAR
endif

ifdef NEED_BASE64
OBJS += ../src/utils/base64.o
endif


OBJS += ../src/common/ieee802_11_common.o
OBJS += ../src/common/hw_features_common.o

ifdef NEED_EAP_COMMON
OBJS += ../src/eap_common/eap_common.o
endif

ifndef CONFIG_MAIN
CONFIG_MAIN=main
endif

ifdef CONFIG_DEBUG_SYSLOG
CFLAGS += -DCONFIG_DEBUG_SYSLOG
ifdef CONFIG_DEBUG_SYSLOG_FACILITY
CFLAGS += -DLOG_HOSTAPD="$(CONFIG_DEBUG_SYSLOG_FACILITY)"
endif
endif

ifdef CONFIG_DEBUG_LINUX_TRACING
CFLAGS += -DCONFIG_DEBUG_LINUX_TRACING
endif

ifdef CONFIG_DEBUG_FILE
CFLAGS += -DCONFIG_DEBUG_FILE
endif

ifdef CONFIG_DELAYED_MIC_ERROR_REPORT
CFLAGS += -DCONFIG_DELAYED_MIC_ERROR_REPORT
endif

ifdef CONFIG_FIPS
CFLAGS += -DCONFIG_FIPS
ifneq ($(CONFIG_TLS), openssl)
ifneq ($(CONFIG_TLS), wolfssl)
$(error CONFIG_FIPS=y requires CONFIG_TLS=openssl)
endif
endif
endif

OBJS += $(SHA1OBJS) $(DESOBJS)

OBJS_p += $(SHA1OBJS)
OBJS_p += $(SHA256OBJS)
OBJS_priv += $(SHA1OBJS)


ifdef CONFIG_AUTOSCAN_EXPONENTIAL
CFLAGS += -DCONFIG_AUTOSCAN_EXPONENTIAL
OBJS += autoscan_exponential.o
NEED_AUTOSCAN=y
endif

ifdef CONFIG_AUTOSCAN_PERIODIC
CFLAGS += -DCONFIG_AUTOSCAN_PERIODIC
OBJS += autoscan_periodic.o
NEED_AUTOSCAN=y
endif

ifdef NEED_AUTOSCAN
CFLAGS += -DCONFIG_AUTOSCAN
OBJS += autoscan.o
endif

ifdef CONFIG_EXT_PASSWORD_TEST
OBJS += ../src/utils/ext_password_test.o
CFLAGS += -DCONFIG_EXT_PASSWORD_TEST
NEED_EXT_PASSWORD=y
endif

ifdef NEED_EXT_PASSWORD
OBJS += ../src/utils/ext_password.o
CFLAGS += -DCONFIG_EXT_PASSWORD
endif

ifdef NEED_GAS_SERVER
OBJS += ../src/common/gas_server.o
CFLAGS += -DCONFIG_GAS_SERVER
NEED_GAS=y
endif

ifdef NEED_GAS
OBJS += ../src/common/gas.o
OBJS += gas_query.o
CFLAGS += -DCONFIG_GAS
NEED_OFFCHANNEL=y
endif

ifdef NEED_OFFCHANNEL
OBJS += offchannel.o
CFLAGS += -DCONFIG_OFFCHANNEL
endif

ifdef NEED_JSON
OBJS += ../src/utils/json.o
CFLAGS += -DCONFIG_JSON
endif

ifdef CONFIG_MODULE_TESTS
CFLAGS += -DCONFIG_MODULE_TESTS
OBJS += wpas_module_tests.o
OBJS += ../src/utils/utils_module_tests.o
OBJS += ../src/common/common_module_tests.o
OBJS += ../src/crypto/crypto_module_tests.o
ifdef CONFIG_WPS
OBJS += ../src/wps/wps_module_tests.o
endif
endif

OBJS += ../src/drivers/driver_common.o
OBJS_priv += ../src/drivers/driver_common.o

OBJS_t := $(OBJS) $(OBJS_l2) eapol_test.o
OBJS_t += ../src/radius/radius_client.o
OBJS_t += ../src/radius/radius.o
OBJS_t2 := $(OBJS) $(OBJS_l2) preauth_test.o

OBJS_nfc := $(OBJS) $(OBJS_l2) nfc_pw_token.o
OBJS_nfc += $(OBJS_d) ../src/drivers/drivers.o

OBJS += $(CONFIG_MAIN).o

ifdef CONFIG_PRIVSEP
OBJS_priv += $(OBJS_d) ../src/drivers/drivers.o
OBJS_priv += $(OBJS_l2)
OBJS_priv += ../src/utils/os_$(CONFIG_OS).o
OBJS_priv += ../src/utils/$(CONFIG_ELOOP).o
OBJS_priv += ../src/utils/common.o
OBJS_priv += ../src/utils/wpabuf.o
ifdef CONFIG_DRIVER_NL80211
OBJS_priv += ../src/common/ieee802_11_common.o
endif
OBJS += ../src/l2_packet/l2_packet_privsep.o
OBJS += ../src/drivers/driver_privsep.o
else
OBJS += $(OBJS_d) ../src/drivers/drivers.o
OBJS += $(OBJS_l2)
endif

ifdef CONFIG_NDIS_EVENTS_INTEGRATED
CFLAGS += -DCONFIG_NDIS_EVENTS_INTEGRATED
OBJS += ../src/drivers/ndis_events.o
EXTRALIBS += -loleaut32 -lole32 -luuid
ifdef PLATFORMSDKLIB
EXTRALIBS += $(PLATFORMSDKLIB)/WbemUuid.Lib
else
EXTRALIBS += WbemUuid.Lib
endif
endif

ifdef CONFIG_FST
CFLAGS += -DCONFIG_FST
ifdef CONFIG_FST_TEST
CFLAGS += -DCONFIG_FST_TEST
endif
FST_OBJS += ../src/fst/fst.o
FST_OBJS += ../src/fst/fst_session.o
FST_OBJS += ../src/fst/fst_iface.o
FST_OBJS += ../src/fst/fst_group.o
FST_OBJS += ../src/fst/fst_ctrl_aux.o
ifdef CONFIG_CTRL_IFACE
FST_OBJS += ../src/fst/fst_ctrl_iface.o
endif
OBJS += $(FST_OBJS)
OBJS_t += $(FST_OBJS)
OBJS_t2 += $(FST_OBJS)
OBJS_nfc += $(FST_OBJS)
endif

ifdef CONFIG_WEP
CFLAGS += -DCONFIG_WEP
endif

ifdef CONFIG_NO_TKIP
CFLAGS += -DCONFIG_NO_TKIP
endif

ifndef LDO
LDO=$(CC)
endif

Q=@
E=echo
ifeq ($(V), 1)
Q=
E=true
endif
ifeq ($(QUIET), 1)
Q=@
E=true
endif

dynamic_eap_methods: $(EAPDYN)

../src/drivers/build.wpa_supplicant:
	@if [ -f ../src/drivers/build.hostapd ]; then \
		$(MAKE) -C ../src/drivers clean; \
	fi
	@touch ../src/drivers/build.wpa_supplicant

BCHECK=../src/drivers/build.wpa_supplicant

wpa_priv: $(BCHECK) $(OBJS_priv)
	$(Q)$(LDO) $(LDFLAGS) -o wpa_priv $(OBJS_priv) $(LIBS)
	@$(E) "  LD " $@

$(OBJS_c) $(OBJS_t) $(OBJS_t2) $(OBJS) $(BCHECK) $(EXTRA_progs): .config

wpa_supplicant: $(BCHECK) $(OBJS) $(EXTRA_progs)
	$(Q)$(LDO) $(LDFLAGS) -o wpa_supplicant $(OBJS) $(LIBS) $(EXTRALIBS)
	@$(E) "  LD " $@

eapol_test: $(OBJS_t)
	$(Q)$(LDO) $(LDFLAGS) -o eapol_test $(OBJS_t) $(LIBS)
	@$(E) "  LD " $@

preauth_test: $(OBJS_t2)
	$(Q)$(LDO) $(LDFLAGS) -o preauth_test $(OBJS_t2) $(LIBS)
	@$(E) "  LD " $@

wpa_passphrase: $(OBJS_p)
	$(Q)$(LDO) $(LDFLAGS) -o wpa_passphrase $(OBJS_p) $(LIBS_p) $(LIBS)
	@$(E) "  LD " $@

wpa_cli: $(OBJS_c)
	$(Q)$(LDO) $(LDFLAGS) -o wpa_cli $(OBJS_c) $(LIBS_c)
	@$(E) "  LD " $@

LIBCTRL += ../src/utils/os_$(CONFIG_OS).o
LIBCTRL += ../src/utils/common.o
LIBCTRLSO += ../src/utils/os_$(CONFIG_OS).c
LIBCTRLSO += ../src/utils/common.c

libwpa_client.a: $(LIBCTRL)
	$(Q)rm -f $@
	$(Q)$(AR) crs $@ $?
	@$(E) "  AR " $@

libwpa_client.so: $(LIBCTRLSO)
	@$(E) "  CC  $@ ($^)"
	$(Q)$(CC) $(LDFLAGS) -o $@ $(CFLAGS) -shared -fPIC $^

libwpa_test1: libwpa_test.o libwpa_client.a
	$(Q)$(LDO) $(LDFLAGS) -o libwpa_test1 libwpa_test.o libwpa_client.a $(LIBS_c)
	@$(E) "  LD " $@

libwpa_test2: libwpa_test.o libwpa_client.so
	$(Q)$(LDO) $(LDFLAGS) -o libwpa_test2 libwpa_test.o -L. -lwpa_client $(LIBS_c)
	@$(E) "  LD " $@

nfc_pw_token: $(OBJS_nfc)
	$(Q)$(LDO) $(LDFLAGS) -o nfc_pw_token $(OBJS_nfc) $(LIBS)
	@$(E) "  LD " $@

win_if_list: win_if_list.c
	$(Q)$(LDO) $(LDFLAGS) -o $@ win_if_list.c $(CFLAGS) $(LIBS_w)
	@$(E) "  LD " $@

eap_psk.so: ../src/eap_peer/eap_psk.c ../src/eap_common/eap_psk_common.c
	$(CC) $(LDFLAGS) -o $@ $(CFLAGS) -shared -rdynamic -fPIC $^ \
		-Deap_peer_psk_register=eap_peer_method_dynamic_init

eap_pax.so: ../src/eap_peer/eap_pax.c ../src/eap_common/eap_pax_common.c
	$(CC) $(LDFLAGS) -o $@ $(CFLAGS) -shared -rdynamic -fPIC $^ \
		-Deap_peer_pax_register=eap_peer_method_dynamic_init

eap_sake.so: ../src/eap_peer/eap_sake.c ../src/eap_common/eap_sake_common.c
	$(CC) $(LDFLAGS) -o $@ $(CFLAGS) -shared -rdynamic -fPIC $^ \
		-Deap_peer_sake_register=eap_peer_method_dynamic_init

eap_wsc.so: ../src/eap_peer/eap_wsc.c ../src/eap_common/eap_wsc_common.c ../src/wps/wps.c
	$(CC) $(LDFLAGS) -o $@ $(CFLAGS) -shared -rdynamic -fPIC $^ \
		-Deap_peer_wsc_register=eap_peer_method_dynamic_init

eap_ikev2.so: ../src/eap_peer/eap_ikev2.c ../src/eap_peer/ikev2.c ../src/eap_common/eap_ikev2_common.o ../src/eap_common/ikev2_common.c
	$(CC) $(LDFLAGS) -o $@ $(CFLAGS) -shared -rdynamic -fPIC $^ \
		-Deap_peer_ikev2_register=eap_peer_method_dynamic_init

eap_eke.so: ../src/eap_peer/eap_eke.c ../src/eap_common/eap_eke_common.c
	$(CC) $(LDFLAGS) -o $@ $(CFLAGS) -shared -rdynamic -fPIC $^ \
		-Deap_peer_eke_register=eap_peer_method_dynamic_init

%.so: %.c
	$(CC) $(LDFLAGS) -o $@ $(CFLAGS) -shared -rdynamic -fPIC $< \
		-D$(*F:eap_%=eap_peer_%)_register=eap_peer_method_dynamic_init

ifdef CONFIG_CODE_COVERAGE
%.o: %.c
	@$(E) "  CC " $<
	$(Q)cd $(dir $@); $(CC) -c -o $(notdir $@) $(CFLAGS) $(notdir $<)
else
%.o: %.c
	$(Q)$(CC) -c -o $@ $(CFLAGS) $<
	@$(E) "  CC " $<
endif

%.service: %.service.in
	$(Q)sed -e 's|\@BINDIR\@|$(BINDIR)|g' $< >$@
	@$(E) "  sed" $<

%@.service: %.service.arg.in
	$(Q)sed -e 's|\@BINDIR\@|$(BINDIR)|g' $< >$@
	@$(E) "  sed" $<

wpa_supplicant.exe: wpa_supplicant
	mv -f $< $@
wpa_cli.exe: wpa_cli
	mv -f $< $@
wpa_passphrase.exe: wpa_passphrase
	mv -f $< $@
win_if_list.exe: win_if_list
	mv -f $< $@
eapol_test.exe: eapol_test
	mv -f $< $@

WINALL=wpa_supplicant.exe wpa_cli.exe wpa_passphrase.exe win_if_list.exe

windows-bin: $(WINALL)
	$(STRIP) $(WINALL)

wpa_gui:
	@echo "wpa_gui has been removed - see wpa_gui-qt4 for replacement"

wpa_gui-qt4/Makefile:
	qmake -o wpa_gui-qt4/Makefile wpa_gui-qt4/wpa_gui.pro

wpa_gui-qt4/lang/wpa_gui_de.qm: wpa_gui-qt4/lang/wpa_gui_de.ts
	lrelease wpa_gui-qt4/wpa_gui.pro

wpa_gui-qt4: wpa_gui-qt4/Makefile wpa_gui-qt4/lang/wpa_gui_de.qm
	$(MAKE) -C wpa_gui-qt4

FIPSDIR=/usr/local/ssl/fips-2.0
FIPSLD=$(FIPSDIR)/bin/fipsld
fips:
	$(MAKE) CC=$(FIPSLD) FIPSLD_CC="$(CC)"

lcov-html: wpa_supplicant.gcda
	lcov -c -d .. > lcov.info
	genhtml lcov.info --output-directory lcov-html

clean:
	$(MAKE) -C ../src clean
	rm -f core *~ *.o *.d *.gcno *.gcda *.gcov
	rm -f eap_*.so $(ALL) $(WINALL) eapol_test preauth_test
	rm -f wpa_priv
	rm -f nfc_pw_token
	rm -f lcov.info
	rm -rf lcov-html
	rm -f libwpa_client.a
	rm -f libwpa_client.so
	rm -f libwpa_test1 libwpa_test2

-include $(OBJS:%.o=%.d)
