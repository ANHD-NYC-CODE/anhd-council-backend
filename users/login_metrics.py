from datetime import date

# First production deploy with portal sign-in metrics (login_count / login_days).
# CSV and admin copy use this so clients know earlier zeros are not historical data.
PORTAL_LOGIN_METRICS_START_DATE = date(2026, 11, 2)
