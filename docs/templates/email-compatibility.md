# Email Template Compatibility Guide

Reference document for PulseCore email templates. Covers known rendering issues,
root causes, applied fixes, and authoring standards to ensure consistent display
across email clients, including Gmail (current SMTP provider).

---

## Issues Found and Resolved

### 1. CSS Not Rendered — Pseudo-elements and Positioning

**Affected:** `waitlist.html`, `invite.html` (prior versions)

**Root cause:** Email clients — including Gmail web and Outlook — do not support several
modern CSS features commonly used in web development:

| CSS feature | Reason for failure |
|---|---|
| `::before` / `::after` | Pseudo-elements are ignored by virtually all email clients |
| `position: absolute` / `relative` | Not supported in Gmail, Outlook, or Apple Mail on iOS |
| `z-index` | Depends on `position`, which is unsupported |
| SVG inside `::before` (dot pattern) | Silently discarded by all email renderers |
| `text-shadow` | Partial support — ignored in Outlook |
| `transform: translateY()` | Not supported in any major email client |
| `transition` / `animation` | Ignored universally |

**Fix applied:** All pseudo-elements and CSS positioning were removed. Replaced with
standard `display: inline-block`, margins, and padding.

---

### 2. Missing Jinja2 Variable — Email Silently Not Sent

**Affected:** `invite.html` — endpoint `POST /v1/waitlist/invite`

**Root cause:** The template referenced `{{ website_url }}` in the footer (Privacy and Terms links),
but the `send_invite()` method in the controller did not include `website_url` in its
`template_data` dictionary. Jinja2 raised an `UndefinedError` at render time. The dispatcher
caught the exception and returned `success: False` — the endpoint responded with HTTP 201
but the email was never sent.

**Fix applied:** Added `"website_url": settings.WEBSITE_URL` to the `template_data`
block inside `send_invite()`.

**Key lesson:** Every Jinja2 variable referenced in a template must have a corresponding
key in the controller's `template_data`. Variables used in footers and conditional blocks
are especially easy to miss.

---

### 3. Plain Text Displayed Instead of HTML — Inverted multipart/alternative Order

**Affected:** `waitlist.html`, `invite.html`

**Symptom:** The email arrived as unstyled plain text, including raw HTML tags such as
`<strong>CRM</strong>` visible in the body. The OTP template was not affected.

**Root cause:** The `SmtpEmailProvider` was building the MIME message in the wrong order.
According to RFC 2046, email clients display the **last** part of a `multipart/alternative`
message that they are capable of rendering. The provider was calling:

```python
message.set_content(payload.body_html, subtype="html")   # first part
message.add_alternative(payload.body_text, subtype="plain")  # last part — shown by client
```

This caused clients to prefer the plain text version over the HTML version.

The OTP template was not affected because its controller does not generate a `body_text`
value, so the `multipart/alternative` block was never triggered and the email was sent
as a simple `text/html` message.

**Fix applied:** The order was inverted in `email_smtp.py` — plain text is now set first
as the fallback, and HTML is added as the last (preferred) alternative:

```python
message.set_content(payload.body_text, subtype="plain")   # first — fallback
message.add_alternative(payload.body_html, subtype="html") # last — preferred by clients
```

**Key lesson:** When building `multipart/alternative` emails, always place the HTML part
last. Clients render the last part they support — plain text must come first, HTML last.

---

## Authoring Standards for New Templates

### Required practices

- Apply inline styles to every element where color, background, padding, font-size, or
  border-radius matter. These properties must not rely solely on `<style>` block classes.
- Reserve the `<style>` block for the CSS reset (`* { margin: 0 }`) and `@media` responsive rules only.
- Set `max-width: 600px` with `margin: auto` on the outermost container.
- Use `display: inline-block` for badges and call-to-action buttons.
- Verify that every Jinja2 variable in the template has a corresponding entry in the
  controller's `template_data` before deploying.

### Prohibited practices

- `::before` and `::after` pseudo-elements — use real HTML elements instead.
- `position: absolute`, `relative`, or `fixed`.
- `z-index`.
- `transform`, `transition`, or `animation` properties.
- `text-shadow` on critical text (decorative only, not relied upon for legibility).
- SVG defined inside CSS — use an `<img>` tag or inline `<svg>` element if necessary.
- Jinja2 variables without a default filter when the controller may omit them
  (use `{{ variable | default('') }}` as a safeguard).

---

## Client Support Reference

| CSS feature | Gmail web | Outlook desktop | Apple Mail | Gmail mobile |
|---|---|---|---|---|
| `<style>` block | Supported | Partial | Supported | Supported |
| Inline styles | Supported | Supported | Supported | Supported |
| `background: linear-gradient` | Supported | Not supported | Supported | Supported |
| `border-radius` | Supported | Not supported | Supported | Supported |
| `::before` / `::after` | Not supported | Not supported | Supported | Not supported |
| `position` / `z-index` | Not supported | Not supported | Supported | Not supported |
| `@media` queries | Supported | Partial | Supported | Supported |

Outlook renders a flat but functional layout — gradients and border-radius degrade
gracefully. Colors and spacing defined as inline styles are preserved in all clients.

---

## Gmail SMTP — Specific Notes

- The `<style>` block is respected in Gmail web but may be stripped by the mobile client.
- Inline styles are always honored in Gmail regardless of client or platform.
- Gmail does not support `position`, `z-index`, or pseudo-elements in any context.
- `background: linear-gradient` renders correctly in Gmail web and the mobile app.

For SMTP configuration details see: [`docs/settings/email_google.md`](../settings/email_google.md)

---

## Pre-deployment Checklist

- [ ] Every Jinja2 variable in the template has a corresponding key in `template_data`
- [ ] Critical styles (color, background, padding) are applied as inline styles
- [ ] No `::before`, `::after`, `position`, or `z-index` are present
- [ ] If `body_text` is provided, verify the MIME order: plain text first, HTML last
- [ ] Tested in Gmail web and a mobile client
- [ ] Visual identity follows PulseCore brand color (`#0082B9`)
