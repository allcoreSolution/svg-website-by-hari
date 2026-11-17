# Gmail SMTP Setup & Configuration Guide — Sky Vision Group

This document explains how to set up Gmail SMTP for sending real transactional and bulk announcement emails from the Sky Vision Group admin dashboard.

---

## 1. Overview

The Bulk Messaging module supports delivering messages via:
1. **Dashboard Inbox** (Internal portal notifications — always delivered instantly).
2. **Email (Gmail SMTP)** — Sends personalized HTML & Plain-text emails to candidate and employer inboxes.

When `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are left blank in `.env`, the system operates in **Test Mode (Console Backend)**. Sent emails are logged to the terminal console and will not be sent to real recipients.

---

## 2. Generating a Google App Password

Google requires a **16-character App Password** when connecting via SMTP (your normal account password will be rejected with an authentication error).

### Step-by-Step Instructions:
1. Log into your Google Account (e.g. `your-company@gmail.com`).
2. Go to **Security Settings**: [myaccount.google.com/security](https://myaccount.google.com/security).
3. Ensure **2-Step Verification** is turned **ON** for your account.
4. Search for **App Passwords** or visit: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
5. Enter an App Name (e.g., `Sky Vision Dashboard`).
6. Click **Create**. Google will display a 16-character code (e.g. `abcd efgh ijkl mnop`).
7. Copy this 16-character code **without spaces**.

---

## 3. Configuring `.env` File

Open or create the `.env` file in your Django project root (`skyvision/.env`) and add the following configuration:

```env
# Email Settings (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL="Sky Vision Group <your-email@gmail.com>"
EMAIL_TIMEOUT=20

# Communication Limits & Safety Controls
COMM_EMAIL_DAILY_LIMIT=400        # Maximum emails per 24h day (keeps below Gmail's 500 limit)
COMM_EMAIL_BATCH_SIZE=20          # Recipients sent per SMTP connection
COMM_EMAIL_DELAY_SECONDS=1        # Pause in seconds between email batches
COMM_REPLY_TO=info@skyvisiongroup.in
COMM_ENABLE_SMS_WHATSAPP=False    # Enable SMS/WhatsApp channels (default: False)
COMM_STALE_SENDING_MINUTES=10     # Threshold (minutes) after which inactive 'Sending' broadcasts become 'Interrupted'
COMM_MAX_ATTACHMENT_MB=5          # Maximum allowed attachment size in MB (PDF, DOC, DOCX, JPG, PNG)
```

---

## 4. Built-in Safety & Protection Features

To prevent account suspension, header injection, or server crashes, the engine includes:

- **Daily Cap Enforcement (400 emails/day)**: Keeps total sent emails safely below Gmail's 500/day free limit.
- **Connection Batching**: Opens 1 SMTP connection per 20 recipients, pauses 1 second, then opens the next batch.
- **Single Recipient Delivery**: Emails are sent individually (`to=[recipient_email]`). Recipients cannot see each other.
- **Authentication Failure Protection**: If credentials fail (`SMTPAuthenticationError`), sending halts immediately to prevent repeated invalid login attempts.
- **Recipient Snapshotting & Retries**: Resolves target recipients up front into `MessageRecipient` rows. Retries process *only* failed rows without re-sending to succeeded recipients.
- **Opt-Out & Deduplication Skipping**: Opted-out accounts (`email_notifications_enabled=False`) and duplicate emails within a broadcast are marked as `Skipped` with clear reasons rather than `Failed`.
- **Heartbeat & Daemon Recovery**: Broadcasts record a `last_activity_at` timestamp per batch. Any broadcast left in `Sending` for >10 minutes (due to server restart or worker crash) is automatically marked as `Interrupted` and can be resumed.
- **Management Command**: Run `python manage.py process_bulk_messages` via Windows Task Scheduler or Linux cron to automatically resume pending broadcasts.
- **Emergency Stop**: Admin can click "Stop Sending" at any time from the detail page to immediately halt outbound processing.

---

## 5. Testing & Verification

1. Go to the Admin Dashboard: `http://127.0.0.1:8000/admin-panel/communication/compose/`.
2. Look at the top status bar:
   - If configured properly, it will display: **Gmail SMTP Connected: your-email@gmail.com** along with your daily limit usage.
3. Click **Send Test Email**, enter your email, and click **Send Test Now**.
4. Check your email inbox to verify delivery.

---

## 6. Troubleshooting Common Errors

| Error Message | Cause | Solution |
| :--- | :--- | :--- |
| `535 5.7.8 Username and Password not accepted` | Invalid Gmail address or using normal Google password. | Enable 2FA on Google account and generate a 16-char App Password. |
| `Daily email quota limit reached (400/day)` | Daily limit cap reached. | Wait until tomorrow or increase `COMM_EMAIL_DAILY_LIMIT` if using Google Workspace paid tier. |
| `SMTP connection timed out` | Firewall or port 587 blocked. | Check server outbound network access to `smtp.gmail.com:587`. |
| `Invalid email address format` | Recipient email is malformed. | System marks that single recipient as `Failed` and continues sending to others. |

---

## 7. Scaling Up: Custom Domain SMTP Providers (Brevo, SendGrid, Amazon SES)

When transitioning from Gmail SMTP to a dedicated transactional email provider (e.g. Brevo, SendGrid, Amazon SES, Mailgun), **zero Python code modifications are needed**. All adjustments are made entirely in your `skyvision/.env` file:

```env
# Example Brevo (Sendinblue) Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=7f123456@smtp-brevo.com
EMAIL_HOST_PASSWORD=your_brevo_smtp_key_here
DEFAULT_FROM_EMAIL="Sky Vision Group <info@skyvisiongroup.in>"
COMM_EMAIL_DAILY_LIMIT=10000        # Increase or remove daily ceiling per your paid quota
```

### Essential DNS Deliverability Setup (Prevent Spam Flagging)
To ensure near 100% inbox placement into recipient Primary inboxes (and avoid Spam/Junk classification), publish these DNS records on your domain (e.g., `skyvisiongroup.in`):

1. **SPF (Sender Policy Framework)**:
   Add or update a `TXT` record on your root domain:
   ```text
   v=spf1 include:spf.sendinblue.com include:_spf.google.com ~all
   ```
2. **DKIM (DomainKeys Identified Mail)**:
   Add the public key `TXT` or `CNAME` records provided in your Brevo/SendGrid sender domain settings. This cryptographically signs every email.
3. **DMARC (Domain-based Message Authentication, Reporting, and Conformance)**:
   Add a `TXT` record at host `_dmarc.skyvisiongroup.in`:
   ```text
   v=DMARC1; p=none; rua=mailto:dmarc-reports@skyvisiongroup.in
   ```

---

## 8. Automated Production Scheduling (`process_bulk_messages`)

For automated daemon recovery, resuming pending batches, and processing queued broadcasts without manual admin intervention:

### On Windows Server (Task Scheduler)
Create a Scheduled Task running every 10 minutes:
- **Program/script**: `python.exe` (or path to your virtual environment `python.exe`)
- **Add arguments**: `manage.py process_bulk_messages`
- **Start in**: `D:\office project\skyvisiongoc\svg_final\skyvision`

Or via PowerShell:
```powershell
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "manage.py process_bulk_messages" -WorkingDirectory "D:\office project\skyvisiongoc\svg_final\skyvision"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 10)
Register-ScheduledTask -TaskName "SkyVision_ProcessBulkMessages" -Action $action -Trigger $trigger -Description "Resumes pending bulk messages and detects interrupted broadcasts"
```

### On Linux (Cron)
Add a cron job via `crontab -e`:
```bash
*/10 * * * * cd /path/to/skyvision && /path/to/venv/bin/python manage.py process_bulk_messages >> /var/log/skyvision_bulk.log 2>&1
```

