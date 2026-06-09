import argparse
import asyncio
import json
import sys
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.database import Base
from app.models.note import User
from app.models.session import AdminPassword, AdminSession, PasskeyCredential
from app.services.passkey_service import (
    generate_registration_options,
    register_credential,
    reset_credential,
    verify_registration,
)
from app.utils.auth import hash_password


REGISTRATION_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Passkey Registration - Blog Admin</title>
<style>
body { font-family: system-ui, sans-serif; max-width: 500px; margin: 80px auto; padding: 20px; }
h1 { font-size: 24px; margin-bottom: 8px; }
p { color: #666; margin-bottom: 24px; }
button { background: #2563eb; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 16px; cursor: pointer; }
button:hover { background: #1d4ed8; }
button:disabled { background: #94a3b8; cursor: not-allowed; }
.status { margin-top: 16px; padding: 12px; border-radius: 8px; }
.success { background: #dcfce7; color: #166534; }
.error { background: #fef2f2; color: #991b1b; }
.info { background: #eff6ff; color: #1e40af; }
</style>
</head>
<body>
<h1>Passkey Registration</h1>
<p>Register a passkey for administrator authentication on this device.</p>
<button id="register-btn" onclick="register()">Register Passkey</button>
<div id="status"></div>
<script>
const PORT = __PORT__;
async function register() {
  const btn = document.getElementById('register-btn');
  const status = document.getElementById('status');
  btn.disabled = true;
  status.className = 'status info';
  status.textContent = 'Requesting registration options...';
  try {
    const optsRes = await fetch('/api/passkey/register/options');
    const opts = await optsRes.json();
    const publicKey = opts.publicKey;
    publicKey.challenge = Uint8Array.from(atob(publicKey.challenge.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0)).buffer;
    publicKey.user.id = Uint8Array.from(atob(publicKey.user.id.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0)).buffer;
    status.textContent = 'Please complete the passkey prompt on your device...';
    const cred = await navigator.credentials.create({ publicKey });
    const attestation = {
      id: cred.id,
      rawId: btoa(String.fromCharCode(...new Uint8Array(cred.rawId))).replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=+$/, ''),
      type: cred.type,
      response: {
        clientDataJSON: btoa(String.fromCharCode(...new Uint8Array(cred.response.clientDataJSON))).replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=+$/, ''),
        attestationObject: btoa(String.fromCharCode(...new Uint8Array(cred.response.attestationObject))).replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=+$/, ''),
      },
    };
    status.textContent = 'Verifying registration...';
    const deviceName = prompt('Enter a device name (e.g., MacBook Pro, iPhone):') || 'Unknown Device';
    const verifyRes = await fetch('/api/passkey/register/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ attestation, deviceName }),
    });
    const result = await verifyRes.json();
    if (result.success) {
      status.className = 'status success';
      status.innerHTML = 'Passkey registered successfully!<br>Device: ' + deviceName + '<br>You can close this page.';
    } else {
      status.className = 'status error';
      status.textContent = 'Registration failed: ' + (result.error || 'Unknown error');
      btn.disabled = false;
    }
  } catch (e) {
    status.className = 'status error';
    status.textContent = 'Error: ' + e.message;
    btn.disabled = false;
  }
}
</script>
</body>
</html>"""


def create_registration_server(port: int, db_url: str) -> HTTPServer:
    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            if self.path == "/api/passkey/register/options":
                opts = generate_registration_options()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(opts).encode())
            elif self.path == "/" or self.path == "/index.html":
                html = REGISTRATION_HTML.replace("__PORT__", str(port))
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode())
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            if self.path == "/api/passkey/register/verify":
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length))
                attestation = body.get("attestation", {})
                device_name = body.get("deviceName", "Unknown Device")

                result = verify_registration(attestation)
                if not result:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": "Verification failed"}).encode())
                    return

                async def _register():
                    async with session_factory() as session:
                        try:
                            cred = await register_credential(
                                session,
                                result["credential_id"],
                                result["public_key"],
                                device_name,
                            )
                            await session.commit()
                            return True, None
                        except Exception as e:
                            await session.rollback()
                            return False, str(e)

                loop = asyncio.new_event_loop()
                try:
                    ok, err = loop.run_until_complete(_register())
                finally:
                    loop.close()

                if ok:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True}).encode())
                    print("\nPasskey registered successfully!")
                else:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": err}).encode())

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

    return HTTPServer(("127.0.0.1", port), Handler)


def cmd_register_passkey(args):
    port = args.port
    settings = get_settings()
    db_url = settings.DATABASE_URL

    print(f"Starting passkey registration server on http://127.0.0.1:{port}")
    print("Opening browser... Press Ctrl+C to cancel.\n")

    server = create_registration_server(port, db_url)

    def _open_browser():
        import time
        time.sleep(0.5)
        webbrowser.open(f"http://127.0.0.1:{port}")

    threading.Thread(target=_open_browser, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nRegistration cancelled.")
    finally:
        server.server_close()


def cmd_reset_passkey(args):
    settings = get_settings()
    db_url = settings.DATABASE_URL

    confirm = input("This will remove the existing passkey. Type 'yes' to confirm: ")
    if confirm.lower() != "yes":
        print("Aborted.")
        return

    project_name = input("Type the project path to confirm (e.g., 2025-blog-public): ")
    if project_name != "2025-blog-public" and project_name != Path.cwd().name:
        print("Project path does not match. Aborted.")
        return

    async def _reset():
        engine = create_async_engine(db_url)
        async with async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)() as session:
            result = await reset_credential(session)
            await session.commit()
            return result

    loop = asyncio.new_event_loop()
    try:
        removed = loop.run_until_complete(_reset())
    finally:
        loop.close()

    if removed:
        print("Passkey removed successfully.")
    else:
        print("No passkey found to remove.")


def cmd_set_password(args):
    settings = get_settings()
    db_url = settings.DATABASE_URL

    import getpass
    password = getpass.getpass("Enter new admin password (min 6 chars): ")
    if len(password) < 6:
        print("Password must be at least 6 characters. Aborted.")
        return
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match. Aborted.")
        return

    async def _set_password():
        engine = create_async_engine(db_url)
        async with async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)() as session:
            result = await session.execute(select(AdminPassword).limit(1))
            admin_pw = result.scalar_one_or_none()
            pw_hash = hash_password(password)
            if admin_pw:
                admin_pw.password_hash = pw_hash
                session.add(admin_pw)
            else:
                admin_pw = AdminPassword(username="admin", password_hash=pw_hash)
                session.add(admin_pw)

            result = await session.execute(select(User).where(User.is_admin == True))
            admin_user = result.scalars().first()
            if admin_user:
                admin_user.password_hash = pw_hash
                session.add(admin_user)

            await session.commit()

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_set_password())
    finally:
        loop.close()

    print("Admin password updated successfully.")


def cmd_reset_password(args):
    settings = get_settings()
    db_url = settings.DATABASE_URL

    confirm = input("This will clear the admin password. Type 'yes' to confirm: ")
    if confirm.lower() != "yes":
        print("Aborted.")
        return

    async def _reset():
        engine = create_async_engine(db_url)
        async with async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)() as session:
            result = await session.execute(select(AdminPassword))
            admin_pw = result.scalar_one_or_none()
            if admin_pw:
                await session.delete(admin_pw)

            result = await session.execute(select(User).where(User.is_admin == True))
            admin_user = result.scalars().first()
            if admin_user:
                admin_user.password_hash = "disabled"
                session.add(admin_user)

            await session.commit()

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_reset())
    finally:
        loop.close()

    print("Admin password cleared.")


def main():
    parser = argparse.ArgumentParser(description="Blog Admin CLI")
    subparsers = parser.add_subparsers(dest="command")

    reg = subparsers.add_parser("register-passkey", help="Register a new passkey")
    reg.add_argument("--port", type=int, default=2026, help="Local server port (default: 2026)")

    subparsers.add_parser("reset-passkey", help="Remove existing passkey")
    subparsers.add_parser("set-password", help="Set or change admin password")
    subparsers.add_parser("reset-password", help="Clear admin password")

    args = parser.parse_args()

    if args.command == "register-passkey":
        cmd_register_passkey(args)
    elif args.command == "reset-passkey":
        cmd_reset_passkey(args)
    elif args.command == "set-password":
        cmd_set_password(args)
    elif args.command == "reset-password":
        cmd_reset_password(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
