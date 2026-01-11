#!/bin/bash

# Absolute path to your Django project
PROJECT_DIR="/app"
MANAGE_PY="$PROJECT_DIR/manage.py"
LOG_FILE="/tmp/customer_cleanup_log.txt"

TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

DELETED_COUNT=$(python3 "$MANAGE_PY" shell -c "
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

cutoff_date = timezone.now() - timedelta(days=365)

qs = Customer.objects.filter(
    orders__isnull=True
) | Customer.objects.filter(
    orders__created_at__lt=cutoff_date
)

deleted, _ = qs.distinct().delete()
print(deleted)
")

echo \"[$TIMESTAMP] Deleted customers: $DELETED_COUNT\" >> "$LOG_FILE"