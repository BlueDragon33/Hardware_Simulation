"""HS-G0-001 Windows hosted Chromium matrix: real browser, honest gates, no policy bypass.

Scope: four restored historical pages x three viewports. Output is QA evidence
only; a successful smoke is NOT owner acceptance or a G1 visual quality PASS.
"""
import hashlib
import http.server
import json
import platform
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "recovered_prototypes"
OUT = ROOT / "tests" / "runtime_output"
EXPECTED_ZIP = "293048a4f5b50e1848202838ca8028f108e9df1022ea40c746122401178c8b6f"
SCENARIOS = (
    "prototypes/v5_mna_solver/index.html",
    "visual/3d_offline_prototype/index.html",
    "visual/3d_threejs_prototype/index.html",
    "visual/visual_prototype_1/index.html",
)
VIEWPORTS = ((1440, 900), (800, 900), (390, 844))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SOURCE), **kwargs)

    def log_message(self, *_args):
        pass


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "hardware-simulation.windows-offline-qa.v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "host": platform.platform(),
        "python": sys.version,
        "source_expected_sha256": EXPECTED_ZIP,
        "gate": "BLOCKED_UNVERIFIED",
        "cases": [],
        "scope": "Windows standard hosted runner; not user's physical Windows computer",
        "policy": "no browser security-policy override; block all external runtime requests",
    }
    server = None
    try:
        manifest = (ROOT / "archive/source_bundle/SHA256SUMS.txt").read_text(encoding="ascii")
        assert manifest.split()[0] == EXPECTED_ZIP, "Unexpected source manifest SHA"
        subprocess.run([sys.executable, str(ROOT / "tools/rebuild_sources.py")],
                       cwd=ROOT, check=True, timeout=60)
        source_zip = ROOT / "archive/source_bundle/Hardware_Simulation_All_Prototypes_Source.zip"
        digest = hashlib.sha256(source_zip.read_bytes()).hexdigest()
        assert digest == EXPECTED_ZIP, "Rebuilt source archive does not match pinned SHA"
        report["actual_source_sha256"] = digest
        for path in SCENARIOS:
            assert (SOURCE / path).is_file(), "Missing restored entrypoint: " + path
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        port = server.server_address[1]
        origin = "http://127.0.0.1:" + str(port)
        report["local_http_status"] = {}
        for path in SCENARIOS:
            with urlopen(origin + "/" + path, timeout=5) as response:
                report["local_http_status"][path] = response.status
                assert response.status == 200, "HTTP server failed for " + path

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            report["chromium_version"] = browser.version
            for path in SCENARIOS:
                for width, height in VIEWPORTS:
                    context = browser.new_context(viewport={"width": width, "height": height},
                                                  device_scale_factor=1)
                    page = context.new_page()
                    errors, console, external, failed = [], [], [], []
                    page.on("pageerror", lambda e: errors.append(str(e)))
                    page.on("console", lambda m: console.append({"type": m.type, "text": m.text})
                            if m.type in ("error", "warning") else None)
                    page.on("requestfailed", lambda req: failed.append(req.url))

                    def route_handler(route):
                        url = route.request.url
                        if url.startswith(origin + "/"):
                            route.continue_()
                        else:
                            external.append(url)
                            route.abort("blockedbyclient")

                    context.route("**/*", route_handler)
                    record = {
                        "source": path, "viewport": [width, height],
                        "status": "NOT_RUN", "page_errors": errors,
                        "console": console, "external_requests_blocked": external,
                        "failed_requests": failed, "actual_app_screenshot": False,
                    }
                    try:
                        response = page.goto(origin + "/" + path, wait_until="domcontentloaded",
                                             timeout=15000)
                        record["http_status"] = response.status if response else None
                        if not response or response.status != 200:
                            record["status"] = "HTTP_NON_200"
                        else:
                            page.wait_for_timeout(600)
                            record["title"] = page.title()
                            record["canvas_count"] = page.locator("canvas").count()
                            record["body_text_length"] = len(page.locator("body").inner_text())
                            record["has_run_button"] = page.locator("#run").count() > 0
                            if page.locator("#run").count():
                                page.locator("#run").click(timeout=4500)
                                page.wait_for_timeout(1500)
                                if page.locator("#state").count():
                                    record["state_after_run"] = page.locator("#state").inner_text()
                            if "v5_mna" in path:
                                record["solver_after_run"] = page.locator("#pwmv").inner_text()
                                record["probe_ch1"] = page.locator("#nodev").inner_text()
                                record["probe_ch2"] = page.locator("#adcv").inner_text()
                            elif "visual_prototype_1" in path:
                                before = page.locator("#scene").get_attribute("style") or ""
                                box = page.locator("#viewport").bounding_box()
                                if box:
                                    x, y = box["x"] + box["width"] * .45, box["y"] + box["height"] * .5
                                    page.mouse.move(x, y)
                                    page.mouse.down()
                                    page.mouse.move(x + 55, y + 20, steps=6)
                                    page.mouse.up()
                                after = page.locator("#scene").get_attribute("style") or ""
                                record["camera_orbit_transform_changed"] = before != after
                                page.locator("#engineering").click(timeout=4500)
                                record["engineering_mode"] = page.locator("#hudMode").inner_text()
                            else:
                                if page.locator("#viewport").count():
                                    box = page.locator("#viewport").bounding_box()
                                    if box:
                                        x, y = box["x"] + box["width"] * .43, box["y"] + box["height"] * .5
                                        page.mouse.move(x, y)
                                        page.mouse.down()
                                        page.mouse.move(x + 45, y + 20, steps=6)
                                        page.mouse.up()
                                        page.mouse.wheel(0, -120)
                                        record["camera_pointer_input_sent"] = True
                                if page.locator("#btnEngineer").count():
                                    page.locator("#btnEngineer").click(timeout=4500)
                                    record["engineering_button_clicked"] = True
                            if external:
                                record["status"] = "BLOCKED_EXTERNAL_RUNTIME_DEPENDENCY"
                            elif errors:
                                record["status"] = "RUNTIME_JAVASCRIPT_ERROR"
                            elif "v5_mna" in path and record.get("solver_after_run") != "MNA OK":
                                record["status"] = "SIMULATION_SOLVER_NOT_OK"
                            elif not record.get("state_after_run", "").endswith("RUNNING"):
                                record["status"] = "RUNTIME_STATE_NOT_RUNNING"
                            else:
                                record["status"] = "RUNTIME_SMOKE_EXECUTED_NOT_ACCEPTED"
                            safe = path.replace("/", "_").replace(".html", "")
                            name = f"{safe}_{width}x{height}.png"
                            page.screenshot(path=str(OUT / name), full_page=False, timeout=8000)
                            record["screenshot"] = name
                            record["actual_app_screenshot"] = True
                    except Exception as exc:
                        record["exception"] = str(exc).splitlines()[0]
                        app_loaded = record.get("http_status") == 200
                        record["navigation_succeeded"] = app_loaded
                        record["status"] = (
                            "BLOCKED_EXTERNAL_RUNTIME_DEPENDENCY" if external else
                            "INTERACTION_OR_QA_ASSERTION_FAILED" if app_loaded else
                            "BROWSER_NAVIGATION_BLOCKED"
                        )
                        try:
                            name = ("app_error_" if app_loaded else "browser_error_") + path.replace("/", "_") + f"_{width}x{height}.png"
                            page.screenshot(path=str(OUT / name), full_page=False, timeout=4000)
                            if app_loaded:
                                record["screenshot"] = name
                                record["actual_app_screenshot"] = True
                            else:
                                record["diagnostic_only_screenshot"] = name
                        except Exception as shot_exc:
                            record["screenshot_error"] = str(shot_exc).splitlines()[0]
                    finally:
                        report["cases"].append(record)
                        print(path, width, height, record["status"], flush=True)
                        context.close()
            browser.close()
        report["gate"] = ("SMOKE_EXECUTED_NOT_PRODUCT_ACCEPTED"
                          if len(report["cases"]) == 12
                          and all(c["status"] == "RUNTIME_SMOKE_EXECUTED_NOT_ACCEPTED"
                                  for c in report["cases"])
                          else "BLOCKED_OR_FAILED")
    except Exception as exc:
        report["preflight_or_runner_error"] = repr(exc)
        report["gate"] = "BLOCKED_RUNNER"
    finally:
        if server:
            server.shutdown()
            server.server_close()
        (OUT / "windows_qa_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print("FINAL_QA_GATE", report["gate"], "CASE_COUNT", len(report["cases"]), flush=True)
    return 0 if report["gate"] == "SMOKE_EXECUTED_NOT_PRODUCT_ACCEPTED" else 1


if __name__ == "__main__":
    sys.exit(run())
