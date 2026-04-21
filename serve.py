#!/usr/bin/env python3
"""
Euler's Method — Local Network Server
Hosts the site on your LAN, opens the nftables firewall port,
and prints a scannable QR code right in the terminal.

Usage:
    python serve.py              # default port 8080
    python serve.py --port 9000  # custom port
    python serve.py --no-firewall

Dependencies (install once):
    pip install qrcode
"""

import argparse
import http.server
import os
import re
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

# ── colour output ─────────────────────────────────────────────────────────────
try:
    from shutil import get_terminal_size
    COLS = get_terminal_size((80, 24)).columns
except Exception:
    COLS = 80

CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def banner(text, color=CYAN):
    bar = "─" * min(len(text) + 4, COLS)
    print(f"\n{color}{BOLD}{bar}{RESET}")
    print(f"{color}{BOLD}  {text}{RESET}")
    print(f"{color}{BOLD}{bar}{RESET}\n")

def ok(msg):   print(f"  {GREEN}✔  {RESET}{msg}")
def warn(msg): print(f"  {YELLOW}⚠  {RESET}{msg}")
def err(msg):  print(f"  {RED}✘  {RESET}{msg}")
def info(msg): print(f"  {DIM}→  {RESET}{msg}")

# ── helpers ───────────────────────────────────────────────────────────────────

def get_local_ip() -> str:
    """Return the machine's LAN IP, preferring physical/WiFi over VPN/Docker."""
    # Skip ZeroTier (zt*), Docker (docker*), VPN tunnels (tun*, neko-*), loopback
    SKIP = re.compile(r'^(zt[a-z0-9]+|docker\d*|tun\d*|neko-.+|lo)$')
    try:
        result = subprocess.run(
            ["ip", "-o", "-4", "addr", "show"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) < 4:
                continue
            iface = parts[1]
            if SKIP.match(iface):
                continue
            ip = parts[3].split('/')[0]
            if not ip.startswith("127."):
                return ip
    except Exception:
        pass
    # Fallback to UDP trick
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def get_zerotier_ip() -> str | None:
    """
    Detect the ZeroTier virtual interface and return its IPv4 address.
    ZeroTier interface names match: zt[a-z0-9]{8}
    Returns None if no ZeroTier interface is found.
    """
    try:
        result = subprocess.run(
            ["ip", "-o", "-4", "addr", "show"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) < 4:
                continue
            iface = parts[1]
            if re.match(r'^zt[a-z0-9]{8}$', iface):
                return parts[3].split('/')[0]
    except Exception:
        pass
    return None


def open_nftables_port(port: int, zt_iface: str | None = None) -> bool:
    """
    Create a dedicated nftables table 'euler_server' that accepts TCP on *port*
    from ALL interfaces (covers LAN + ZeroTier).
    Returns True if rules were installed, False otherwise.
    """
    if os.geteuid() != 0:
        warn("Not running as root — skipping nftables rules.")
        warn("Run with  sudo python serve.py  to open firewall ports automatically.")
        warn(f"Or open the port manually:  sudo nft add rule inet filter input tcp dport {port} accept")
        return False

    # Drop any stale table from a previous run
    subprocess.run(["nft", "delete", "table", "inet", "euler_server"],
                   capture_output=True)

    cmds = [
        ["nft", "add", "table", "inet", "euler_server"],
        ["nft", "add", "chain", "inet", "euler_server", "input",
         "{ type filter hook input priority -1; policy accept; }"],
        ["nft", "add", "rule", "inet", "euler_server", "input",
         "tcp", "dport", str(port), "accept"],
    ]

    if zt_iface:
        cmds.append(
            ["nft", "add", "rule", "inet", "euler_server", "input",
             "iif", zt_iface, "tcp", "dport", str(port), "accept"]
        )

    all_ok = True
    for cmd in cmds:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            warn(f"nft command failed: {' '.join(cmd)}")
            warn(f"  → {r.stderr.strip()}")
            all_ok = False

    if all_ok:
        ok(f"nftables: table 'euler_server' created — port {port}/tcp open on ALL interfaces")
        if zt_iface:
            ok(f"nftables: explicit ZeroTier rule added for interface '{zt_iface}'")
    else:
        warn("Some nftables rules could not be added — VPN access may not work.")

    return all_ok


def close_nftables_port():
    """Remove the euler_server nftables table we created."""
    if os.geteuid() != 0:
        return
    r = subprocess.run(
        ["nft", "delete", "table", "inet", "euler_server"],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        ok("nftables: 'euler_server' table removed — port closed")
    else:
        warn(f"Could not remove nftables table: {r.stderr.strip()}")


def make_qr_terminal(url: str):
    """Print a scannable QR code to the terminal using Unicode block chars."""
    try:
        import qrcode
    except ImportError:
        warn("'qrcode' not installed — run:  pip install qrcode")
        warn(f"URL: {url}")
        return

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    matrix = qr.get_matrix()
    rows   = len(matrix)
    lines  = []

    for r in range(0, rows, 2):
        line = ""
        for c in range(len(matrix[r])):
            top = matrix[r][c]     if r < rows     else False
            bot = matrix[r+1][c]   if (r+1) < rows else False
            if top and bot:   line += "█"
            elif top:         line += "▀"
            elif bot:         line += "▄"
            else:             line += " "
        lines.append(line)

    width  = len(lines[0]) if lines else 20
    pad    = max((COLS - width) // 2, 2)
    indent = " " * pad

    print(f"\n{CYAN}{BOLD}  Scan to open on your device:{RESET}\n")
    border = indent + "\033[47m\033[30m" + " " * (width + 4) + "\033[0m"
    print(border)
    for line in lines:
        print(indent + f"\033[47m\033[30m  {line}  \033[0m")
    print(border)
    print()


# ── HTTP handler ──────────────────────────────────────────────────────────────

class SiteHandler(http.server.SimpleHTTPRequestHandler):
    """Serve files from the project directory with clean request logs."""

    def handle(self):
        try:
            super().handle()
        except BrokenPipeError:
            pass

    def log_message(self, fmt, *args):
        client = self.address_string()
        code   = args[1] if len(args) > 1 else "?"
        path   = args[0].split('"')[1] if '"' in args[0] else args[0]
        color  = GREEN if str(code).startswith("2") else YELLOW
        print(f"  {DIM}{time.strftime('%H:%M:%S')}{RESET}  "
              f"{color}{code}{RESET}  {client}  {DIM}{path}{RESET}")

    def log_error(self, fmt, *args):
        pass  # silence 404s etc.


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Euler's Method local server")
    parser.add_argument("--port", "-p", type=int, default=8080,
                        help="Port to listen on (default: 8080)")
    parser.add_argument("--no-firewall", action="store_true",
                        help="Skip nftables firewall rule")
    args = parser.parse_args()

    PORT   = args.port
    HOST   = "0.0.0.0"
    LAN_IP = get_local_ip()
    ZT_IP  = get_zerotier_ip()
    URL    = f"http://{LAN_IP}:{PORT}/index.html"
    ZT_URL = f"http://{ZT_IP}:{PORT}/index.html" if ZT_IP else None

    # ── verify index.html exists ───────────────────────────────────────────
    script_dir = Path(__file__).parent.resolve()
    site_file  = script_dir / "index.html"

    if not site_file.exists():
        err(f"index.html not found in {script_dir}")
        err("Make sure serve.py and index.html are in the same folder.")
        sys.exit(1)

    # ── firewall ───────────────────────────────────────────────────────────
    banner("Euler's Method — Local Server", CYAN)

    rule_added = False
    if not args.no_firewall:
        zt_iface = None
        if ZT_IP:
            result = subprocess.run(["ip", "-o", "-4", "addr", "show"],
                                    capture_output=True, text=True)
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 4 and re.match(r'^zt[a-z0-9]{8}$', parts[1]):
                    zt_iface = parts[1]
                    break
        info("Opening nftables firewall port …")
        rule_added = open_nftables_port(PORT, zt_iface=zt_iface)
    else:
        info("Skipping firewall (--no-firewall flag set)")

    # ── start server ───────────────────────────────────────────────────────
    handler = lambda *a, **kw: SiteHandler(*a, directory=str(script_dir), **kw)

    try:
        httpd = http.server.HTTPServer((HOST, PORT), handler)
    except OSError as e:
        err(f"Cannot bind to port {PORT}: {e}")
        err("Try a different port with --port XXXX")
        sys.exit(1)

    ok(f"Server running on port {PORT}")
    ok(f"Local:      http://localhost:{PORT}/index.html")
    ok(f"LAN:        {BOLD}{URL}{RESET}")
    if ZT_IP:
        ok(f"ZeroTier:   {BOLD}{ZT_URL}{RESET}  {DIM}({ZT_IP}){RESET}")
    else:
        warn("ZeroTier:   no ZeroTier interface detected (is ZeroTier running?)")

    # ── QR codes ───────────────────────────────────────────────────────────
    print(f"\n  {CYAN}{BOLD}LAN QR code:{RESET}")
    make_qr_terminal(URL)

    if ZT_URL:
        print(f"  {CYAN}{BOLD}ZeroTier QR code (for remote/VPN devices):{RESET}")
        make_qr_terminal(ZT_URL)

    print(f"  {DIM}Press Ctrl+C to stop{RESET}\n")
    print("  " + "─" * (COLS - 4))
    print(f"  {DIM}Requests:{RESET}")

    # ── serve ─────────────────────────────────────────────────────────────
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n  {YELLOW}Shutting down …{RESET}")
        httpd.shutdown()
        if rule_added:
            info("Removing nftables rule …")
            close_nftables_port()
            ok("Firewall rule removed")
        print(f"  {GREEN}Done. Goodbye!{RESET}\n")


if __name__ == "__main__":
    main()
