# Security recommendations for ClearScan

## UFW (Firewall)
- Only ports 80/tcp (HTTP dashboard) and 22/tcp (SSH) are open.
- All other incoming connections are denied.

## User and File Permissions
- Application runs as a dedicated system user: `clearscan` (no shell, no login).
- All files in `/opt/clearscan/` belong to `clearscan:clearscan` and have permissions 750 (directories) / 640 (config/db).
- Sensitive files (`config.yaml`, `clearscan.db`) are readable only by `clearscan` and group.

## Usage
- Run `bash secure_setup.sh` after deployment.
- For systemd/gunicorn, set `User=clearscan` in the service file.

## Example systemd snippet
```
[Service]
User=clearscan
Group=clearscan
WorkingDirectory=/opt/clearscan
...other options...
```

## Notes
- Never run the application as root.
- Do not expose the dashboard to the public internet without strong passwords and firewall rules.
