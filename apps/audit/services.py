import logging
from .models import AuditLog

logger = logging.getLogger("billing")

def record_audit(request, action, model_name="", object_id="", details=None):
    user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")
    entry = AuditLog.objects.create(user=user, action=action, model_name=model_name, object_id=str(object_id or ""), path=request.path[:500], ip_address=ip, details=details or {})
    logger.info("Audit event | action=%s | model=%s | object=%s | user=%s", action, model_name, object_id, getattr(user, "username", "anonymous"))
    return entry
