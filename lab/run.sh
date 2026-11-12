#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
HERE="$(pwd)"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-webminh27}"
export PYTHONUNBUFFERED=1

LABEL="WEBMIN-H27-SESSIONDB"
WITNESS="WEBMIN-H27-SESSION-KEY"
IMAGE="webmin-lab:2.670"
LOCK="/tmp/webmin-lab-image.lock"
BASE="http://127.0.0.1:18440"
PIN_COMMIT="3a2b2b8671c0669c129f5275b3dd1853106ae02b"
PIN_TAG="2.670"
REPO_URL="${WEBMIN_SRC_URL:-https://github.com/webmin/webmin.git}"
PIN="${HERE}/src"
DOCKERFILE="${HERE}/Dockerfile"

down() {
  echo "== docker compose down -v =="
  docker compose -p "${COMPOSE_PROJECT_NAME}" down -v --remove-orphans || true
}

fail_setup() {
  echo "FAIL ${LABEL} $* ${WITNESS}" | tee poc-last-run.txt
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 webmin || true
  exit 1
}

ensure_pin() {
  if [[ ! -e "${PIN}/.git" ]]; then
    echo "== git clone ${REPO_URL} tag ${PIN_TAG} =="
    GIT_TERMINAL_PROMPT=0 git clone --filter=blob:none --no-checkout "${REPO_URL}" "${PIN}" \
      || fail_setup "clone-failed"
    git -C "${PIN}" fetch --depth 1 origin "refs/tags/${PIN_TAG}:refs/tags/${PIN_TAG}" \
      || fail_setup "fetch-failed"
    git -C "${PIN}" checkout --detach "${PIN_COMMIT}" || fail_setup "checkout-failed"
  fi
  local got
  got="$(git -C "${PIN}" rev-parse HEAD)"
  if [[ "${got}" != "${PIN_COMMIT}" ]]; then
    fail_setup "pin-mismatch got=${got}"
  fi
  if [[ ! -f "${PIN}/miniserv.pl" || ! -f "${PIN}/acl/list_sessions.cgi" ]]; then
    fail_setup "pin-missing"
  fi
  echo "IOC pin=${PIN_TAG} commit=${got}"
}

ensure_image() {
  python3 - "${LOCK}" "${IMAGE}" "${DOCKERFILE}" "${PIN}" <<'PY'
import fcntl
import os
import subprocess
import sys

lock_path, image, dockerfile, src = sys.argv[1:5]
fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o666)
fcntl.flock(fd, fcntl.LOCK_EX)
try:
    inspect = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True,
        check=False,
    )
    if inspect.returncode == 0:
        print(f"IOC reuse-image {image}", flush=True)
        raise SystemExit(0)
    print(f"IOC build-image {image}", flush=True)
    raise SystemExit(
        subprocess.call(["docker", "build", "-t", image, "-f", dockerfile, src])
    )
finally:
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)
PY
}

trap down EXIT

echo "== py_compile poc.py =="
python3 -m py_compile poc.py

echo "== docker compose down (clean) =="
down
docker network prune -f >/dev/null 2>&1 || true

echo "== ensure pin =="
ensure_pin

echo "== ensure ${IMAGE} =="
ensure_image || fail_setup "image-build-failed"

echo "== docker compose up =="
up_ok=0
for attempt in $(seq 1 12); do
  docker network prune -f >/dev/null 2>&1 || true
  if docker compose -p "${COMPOSE_PROJECT_NAME}" up -d; then
    up_ok=1
    break
  fi
  echo "IOC compose-up-retry attempt=${attempt}"
  sleep 8
  down
done
if [[ "${up_ok}" != 1 ]]; then
  fail_setup "compose-up-failed"
fi

echo "== wait ${BASE}/session_login.cgi =="
ready=0
for i in $(seq 1 60); do
  code="$(curl -sS -o /tmp/webmin-h27-ready.html -w '%{http_code}' --max-time 8 \
    "${BASE}/session_login.cgi" || true)"
  if [[ "${code}" == "200" || "${code}" == "401" ]]; then
    ready=1
    echo "IOC login-ready attempt=${i} http=${code}"
    break
  fi
  echo "IOC login-wait attempt=${i} http=${code}"
  sleep 2
done
if [[ "${ready}" != 1 ]]; then
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 webmin || true
  fail_setup "login-not-ready"
fi

echo "== poc.py =="
set +e
python3 ./poc.py | tee poc-last-run.txt
rc=${PIPESTATUS[0]}
set -e

if ! tail -n1 poc-last-run.txt 2>/dev/null | grep -qE '^(SUCCESS|FAIL) '; then
  echo "FAIL ${LABEL} poc-exit=${rc} ${WITNESS}" >> poc-last-run.txt
  rc=1
fi

exit "${rc}"
