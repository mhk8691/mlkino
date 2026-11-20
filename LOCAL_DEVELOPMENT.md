# Running the connected panel

## اجرای بک‌اند روی این سیستم (Linux)

محیط Python در `.venv` و PostgreSQL در `.local/postgres` نصب شده‌اند.
داده‌های دیتابیس محلی در `.local/pgdata` نگه‌داری می‌شوند. این پوشه را حذف نکنید.
PostgreSQL فقط روی `127.0.0.1:5433` گوش می‌دهد و از تنظیمات فعلی Django استفاده می‌کند.

برای اجرای مجدد از پوشه پروژه:

```sh
bash scripts/run-backend-local.sh
```

مستندات API: http://127.0.0.1:8000/api/docs/

برای توقف سرور در ترمینال `Ctrl+C` بزنید. برای توقف دیتابیس:

```sh
LD_LIBRARY_PATH="$PWD/.local/postgres/usr/lib" .local/postgres/usr/bin/pg_ctl -D "$PWD/.local/pgdata" stop
```

دیتابیس اولیه خالی است. برای ساخت حساب مدیر:

```sh
.venv/bin/python manage.py createsuperuser
```

نصب محلی PostgreSQL مخصوص همین Linux است؛ پوشه‌های `.local` و `.venv` وارد Git نمی‌شوند.

Backend (Python dependencies are in `requirements-extra.txt`):

```sh
python3 -m pip install -r requirements-extra.txt
python3 manage.py migrate
python3 manage.py runserver 127.0.0.1:8000
```

Daphne provides HTTP and WebSocket support through `mlkino.asgi.application`.
Frontend: run `npm start` inside `frontend`, and open `http://localhost:3000`.
The local API hostname automatically follows localhost/127.0.0.1 so auth cookies stay on the same site.

برای نصب مجدد وابستگی‌های پنل با نسخه‌های قفل‌شده، از
`npm --prefix frontend ci --legacy-peer-deps` استفاده کنید؛ کتابخانه‌های قدیمی Material UI
به این گزینه سازگاری نیاز دارند. برای اجرای پنل `npm --prefix frontend start` را بزنید
و http://localhost:3000/login را باز کنید. مسیر `/` در حالت توسعه به صفحه ورود همان پنل می‌رود.

## Realtime and calls

The inbox WebSocket is `/ws/inbox/`. Messages are persisted through the scoped REST API
and broadcast after commit. The socket also carries typing, read receipts, deletions,
and WebRTC offer/answer/ICE/end signals. Incoming calls work outside the chat route.
Only conversation members can read messages, download private attachments, or signal a call.

The local channel layer is in-memory for one ASGI process. For multiple server processes,
set `MLKINO_REDIS_URL=redis://127.0.0.1:6379/0` so every process shares notifications.
Production reverse proxies must forward `/ws/` WebSocket upgrades to the ASGI server.

Microphone/camera access requires localhost or HTTPS. For calls across restrictive NATs,
configure a TURN server in the frontend build using the JSON environment variable
`REACT_APP_ICE_SERVERS` (an array of RTCIceServer objects). The default is STUN only.
Browser validation used synthetic camera/microphone streams, two isolated authenticated
contexts, and verified actual peer-connection state for both voice and video.

## Settings and assets

`GET /panel/settings/` is readable to authenticated users; only superadmins can PATCH.
Saved branding, theme, title and SEO metadata are applied through a shared settings provider.
Image uploads use `PANEL_SETTINGS_PUBLIC_BASE_URL`, falling back to the request origin locally.
Generated logo and illustration assets and their prompts are in `frontend/public/assets/README.md`.

## User scope

Superadmins can manage all four categories. Agencies have only `/users/expert` and
its create/detail routes; server queries and writes are scoped through active AgencyExpert
links. Expert creation by an agency binds the expert to that agency. Other roles cannot
access user-management APIs or menu items. Form payloads normalize nested role profiles
and use the backend field names for ownership and professional details.

## Profile and panel redesign

Run `python3 manage.py migrate` before starting the backend. Migration `accounts.0011` adds account preferences, notification history, managed device sessions, and the profile update timestamp. Existing sessions can be upgraded from the device-management page without another password prompt.

The profile page uses `/accounts/profile/` (GET/PATCH), `/accounts/change-password/`, `/accounts/preferences/`, `/accounts/sessions/`, `/accounts/notifications/`, and `/accounts/activity/`. Session revocation invalidates both access and refresh tokens associated with that device. Password changes close previous tracked devices and retain a newly issued current session. Privacy preferences affect contact search and creation of new conversations.

Task lists default to all dates. The dashboard explicitly requests `period=today`; `period=upcoming`, `period=overdue`, `date`, `scope`, `status`, and `search` are available on `/panel/tasks/`. Newly created future tasks stay visible in the task list. Dates use the configured timezone (Tehran by default).

Only superadmins can edit system settings and inspect/export activity logs. Settings persist via `/panel/settings/`; maintenance mode limits panel writes for nonadmins while tickets remain available. Logs support CSV export of filtered results (up to 10,000 rows). Sidebar collapse is saved per browser, while mobile uses a temporary drawer.

Verification: backend role/API tests use an isolated SQLite test database; frontend tests and production build are run locally. Chrome checks cover desktop/mobile layout, task creation and refresh, profile tabs and devices, settings persistence, user/admin ticket replies, agency expert routing, ordinary-role access denial, and passwordless impersonation return.
