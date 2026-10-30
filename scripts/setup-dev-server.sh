#!/usr/bin/env bash
# Sets up the shared "crannog" dev account on the homeserver (Ubuntu 20.04).
#
# - creates a non-sudo user "crannog" with a password
# - allows password SSH for that user ONLY from Tailscale addresses
# - closes other users' home dirs to the crannog user (nginx keeps access)
# - installs git/tmux/sqlite and uv (which brings its own modern Python)
#
# Run on the server:  sudo bash setup-dev-server.sh
# Safe to re-run. Set SKIP_HOME_LOCKDOWN=1 to leave other home dirs alone.
set -euo pipefail

DEV_USER=crannog
APP_PORT=8100
TS_V4=100.64.0.0/10
TS_V6=fd7a:115c:a1e0::/48
SSHD_CONFIG=/etc/ssh/sshd_config
BLOCK_BEGIN="# BEGIN crannog-dev"
BLOCK_END="# END crannog-dev"

die() { echo "error: $*" >&2; exit 1; }
step() { echo; echo "==> $*"; }

[[ $EUID -eq 0 ]] || die "run as root: sudo bash $0"
command -v tailscale >/dev/null || die "tailscale is not installed"
TS_IP=$(tailscale ip -4 2>/dev/null | head -n1) || true
[[ -n $TS_IP ]] || die "tailscale is not up (no 100.x address)"

step "Dev user '$DEV_USER'"
if id "$DEV_USER" &>/dev/null; then
    echo "user already exists"
else
    adduser --disabled-password --gecos "" "$DEV_USER"
fi
chmod 750 "/home/$DEV_USER"
# "L" = locked/no password yet; only prompt then, so re-runs don't reset it
if [[ $(passwd -S "$DEV_USER" | awk '{print $2}') == "L" ]]; then
    echo "Choose the shared password for $DEV_USER (use a long one):"
    passwd "$DEV_USER"
else
    echo "password already set (change it with: sudo passwd $DEV_USER)"
fi

step "Packages"
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    git curl ca-certificates build-essential tmux sqlite3 acl

step "Restricting other home directories"
if [[ ${SKIP_HOME_LOCKDOWN:-0} == 1 ]]; then
    echo "skipped (SKIP_HOME_LOCKDOWN=1)"
else
    for dir in /home/*/; do
        dir=${dir%/}
        [[ $(stat -c %U "$dir") == "$DEV_USER" ]] && continue
        perms=$(stat -c %a "$dir")
        if (( 8#$perms & 8#007 )); then
            chmod o-rwx "$dir"
            # keep nginx able to serve sites that live under this home dir
            id www-data &>/dev/null && setfacl -m u:www-data:x "$dir"
            echo "$dir: $perms -> $(stat -c %a "$dir")"
        else
            echo "$dir: already private"
        fi
    done
fi

step "uv (Python toolchain) for $DEV_USER"
if sudo -u "$DEV_USER" -H bash -lc 'command -v uv' &>/dev/null; then
    echo "uv already installed"
else
    sudo -u "$DEV_USER" -H bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
fi

step "SSH: password login for $DEV_USER from Tailscale only"
backup="$SSHD_CONFIG.bak.$(date +%Y%m%d%H%M%S)"
cp -a "$SSHD_CONFIG" "$backup"
sed -i "/^$BLOCK_BEGIN\$/,/^$BLOCK_END\$/d" "$SSHD_CONFIG"
cat >> "$SSHD_CONFIG" <<EOF
$BLOCK_BEGIN
Match User $DEV_USER Address $TS_V4,$TS_V6
    PasswordAuthentication yes
Match User $DEV_USER Address *,!$TS_V4,!$TS_V6
    PasswordAuthentication no
    PubkeyAuthentication no
    KbdInteractiveAuthentication no
    GSSAPIAuthentication no
    HostbasedAuthentication no
$BLOCK_END
EOF

restore() { cp -a "$backup" "$SSHD_CONFIG"; die "$1 (sshd config restored from $backup)"; }
sshd -t || restore "sshd config is invalid"
effective() { sshd -T -C "user=$DEV_USER,host=check,addr=$1" | awk -v k="$2" '$1==k {print $2}'; }
[[ $(effective "$TS_IP" passwordauthentication) == yes ]] \
    || restore "self-test failed: password login not enabled over Tailscale"
[[ $(effective 192.168.1.50 passwordauthentication) == no &&
   $(effective 192.168.1.50 pubkeyauthentication) == no ]] \
    || restore "self-test failed: $DEV_USER would be reachable from outside Tailscale"
systemctl reload ssh
echo "ok (previous config saved as $backup)"

if tailscale debug prefs 2>/dev/null | grep -q '"RunSSH": true'; then
    echo
    echo "WARNING: Tailscale SSH is enabled on this machine. It takes over port 22"
    echo "on the tailnet and ignores passwords. Disable it with: tailscale set --ssh=false"
fi

step "Workspace"
sudo -u "$DEV_USER" mkdir -p "/home/$DEV_USER/crannog-web"

cat <<EOF

Done.

  Connect:   ssh $DEV_USER@$TS_IP
  Run app:   .venv/bin/uvicorn app:app --reload --host 127.0.0.1 --port $APP_PORT
  Browse:    https://crannog-dev.pascal345.uk (via Cloudflare tunnel)

Next: share this machine with the other developer from the Tailscale admin
console (Machines -> homeserver -> Share), then restrict what shared users can
reach in the access controls (Access controls -> autogroup:shared rule).
EOF
