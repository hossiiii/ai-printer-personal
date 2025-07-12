"""
Comprehensive audit logging and compliance system
"""
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import logging
from sqlalchemy import select, insert
from ..database.models import AuditLog, User
from ..database.connection import get_db_context
from ..config import settings
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

audit_logger = structlog.get_logger("audit")


class AuditEventType(Enum):
    """Types of audit events"""
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_LOCKED = "account_locked"
    
    # Authorization events
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_ESCALATION = "permission_escalation"
    
    # Data events
    DATA_CREATE = "data_create"
    DATA_READ = "data_read"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    
    # API events
    API_CALL = "api_call"
    API_ERROR = "api_error"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    
    # File events
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    FILE_DELETE = "file_delete"
    
    # System events
    SYSTEM_ERROR = "system_error"
    CONFIGURATION_CHANGE = "configuration_change"
    BACKUP_CREATED = "backup_created"
    
    # Compliance events
    DATA_RETENTION_POLICY_APPLIED = "data_retention_applied"
    GDPR_REQUEST = "gdpr_request"
    PII_ACCESS = "pii_access"
    
    # Security events
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SECURITY_VIOLATION = "security_violation"
    MALWARE_DETECTED = "malware_detected"


class ComplianceStandard(Enum):
    """Compliance standards"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"


class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self):
        self.logger = audit_logger
        self._compliance_handlers = {
            ComplianceStandard.GDPR: self._handle_gdpr_audit,
            ComplianceStandard.CCPA: self._handle_ccpa_audit,
            ComplianceStandard.SOC2: self._handle_soc2_audit,
        }
    
    async def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: str = None,
        details: Dict[str, Any] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        compliance_standards: List[ComplianceStandard] = None,
        severity: str = "info"
    ):
        """Log audit event with comprehensive details"""
        
        event_data = {
            "event_type": event_type.value,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action or event_type.value,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "session_id": details.get("session_id") if details else None,
            "severity": severity,
            "environment": "production" if not settings.DEVELOPMENT else "development"
        }
        
        # Add compliance metadata
        if compliance_standards:
            event_data["compliance_standards"] = [std.value for std in compliance_standards]
            
            # Process compliance-specific requirements
            for standard in compliance_standards:
                if standard in self._compliance_handlers:
                    event_data = await self._compliance_handlers[standard](event_data)
        
        # Log to structured logger
        self.logger.info(
            f"Audit event: {event_type.value}",
            **event_data
        )
        
        # Store in database
        await self._store_audit_log(event_data)
        
        # Check for security alerts
        await self._check_security_alerts(event_data)
    
    async def _store_audit_log(self, event_data: Dict[str, Any]):
        """Store audit log in database"""
        try:
            async with get_db_context() as db:
                audit_entry = AuditLog(
                    user_id=event_data.get("user_id"),
                    action=event_data["action"],
                    resource_type=event_data.get("resource_type"),
                    resource_id=event_data.get("resource_id"),
                    details=event_data["details"],
                    ip_address=event_data.get("ip_address"),
                    user_agent=event_data.get("user_agent"),
                    timestamp=datetime.fromisoformat(event_data["timestamp"].replace('Z', '+00:00'))
                )
                
                db.add(audit_entry)
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store audit log: {e}", event_data=event_data)
    
    async def _check_security_alerts(self, event_data: Dict[str, Any]):
        """Check for security alerts based on audit events"""
        event_type = event_data["event_type"]
        user_id = event_data.get("user_id")
        ip_address = event_data.get("ip_address")
        
        # Check for multiple failed login attempts
        if event_type == AuditEventType.LOGIN_FAILURE.value:
            await self._check_brute_force_attack(user_id, ip_address)
        
        # Check for unusual access patterns
        if event_type in [AuditEventType.DATA_READ.value, AuditEventType.DATA_EXPORT.value]:
            await self._check_unusual_access_pattern(user_id, event_data)
        
        # Check for privilege escalation attempts
        if event_type == AuditEventType.ACCESS_DENIED.value:
            await self._check_privilege_escalation(user_id, event_data)
    
    async def _check_brute_force_attack(self, user_id: Optional[int], ip_address: Optional[str]):
        """Check for brute force attack patterns"""
        if not ip_address:
            return
            
        # Count failed login attempts from IP in last 15 minutes
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(minutes=15)
        
        async with get_db_context() as db:
            result = await db.execute(
                select(AuditLog).where(
                    AuditLog.action == "login_failure",
                    AuditLog.ip_address == ip_address,
                    AuditLog.timestamp >= cutoff_time
                )
            )
            
            failed_attempts = result.fetchall()
            
            if len(failed_attempts) >= 5:
                await self.log_event(
                    AuditEventType.SUSPICIOUS_ACTIVITY,
                    user_id=user_id,
                    action="potential_brute_force",
                    details={
                        "failed_attempts": len(failed_attempts),
                        "ip_address": ip_address,
                        "time_window": "15_minutes"
                    },
                    ip_address=ip_address,
                    severity="warning"
                )
    
    async def _check_unusual_access_pattern(self, user_id: Optional[int], event_data: Dict[str, Any]):
        """Check for unusual data access patterns"""
        if not user_id:
            return
            
        # Check for bulk data access
        details = event_data.get("details", {})
        if details.get("bulk_operation") or details.get("record_count", 0) > 100:
            await self.log_event(
                AuditEventType.SUSPICIOUS_ACTIVITY,
                user_id=user_id,
                action="bulk_data_access",
                details={
                    "original_event": event_data,
                    "risk_level": "medium"
                },
                ip_address=event_data.get("ip_address"),
                severity="warning"
            )
    
    async def _check_privilege_escalation(self, user_id: Optional[int], event_data: Dict[str, Any]):
        """Check for privilege escalation attempts"""
        if not user_id:
            return
            
        details = event_data.get("details", {})
        required_role = details.get("required_role")
        user_role = details.get("user_role")
        
        if required_role and user_role and required_role != user_role:
            await self.log_event(
                AuditEventType.SUSPICIOUS_ACTIVITY,
                user_id=user_id,
                action="privilege_escalation_attempt",
                details={
                    "user_role": user_role,
                    "required_role": required_role,
                    "requested_resource": event_data.get("resource_type"),
                    "risk_level": "high"
                },
                ip_address=event_data.get("ip_address"),
                severity="warning"
            )
    
    # Compliance-specific handlers
    async def _handle_gdpr_audit(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GDPR-specific audit requirements"""
        event_data["gdpr_metadata"] = {
            "data_subject_rights": True,
            "lawful_basis": "legitimate_interest",  # This should be determined based on the action
            "retention_period": "7_years",
            "anonymization_required": False
        }
        
        # Check if this involves personal data
        if self._involves_personal_data(event_data):
            event_data["gdpr_metadata"]["personal_data_processing"] = True
            event_data["gdpr_metadata"]["anonymization_required"] = True
        
        return event_data
    
    async def _handle_ccpa_audit(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CCPA-specific audit requirements"""
        event_data["ccpa_metadata"] = {
            "consumer_rights": True,
            "opt_out_available": True,
            "third_party_sharing": False
        }
        return event_data
    
    async def _handle_soc2_audit(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SOC 2-specific audit requirements"""
        event_data["soc2_metadata"] = {
            "control_category": self._get_soc2_control_category(event_data["event_type"]),
            "monitoring_control": True,
            "access_control": True
        }
        return event_data
    
    def _involves_personal_data(self, event_data: Dict[str, Any]) -> bool:
        """Check if the event involves personal data"""
        personal_data_indicators = [
            "email", "phone", "address", "name", "user_profile",
            "audio_file", "document", "transcription"
        ]
        
        resource_type = event_data.get("resource_type", "")
        details = event_data.get("details", {})
        
        return (
            any(indicator in resource_type.lower() for indicator in personal_data_indicators) or
            any(indicator in str(details).lower() for indicator in personal_data_indicators)
        )
    
    def _get_soc2_control_category(self, event_type: str) -> str:
        """Get SOC 2 control category for event type"""
        if event_type.startswith("login") or event_type.startswith("access"):
            return "CC6.1"  # Logical and Physical Access Controls
        elif event_type.startswith("data"):
            return "CC6.7"  # Data Transmission and Disposal
        elif event_type.startswith("system"):
            return "CC7.1"  # System Monitoring
        else:
            return "CC1.4"  # General Controls
    
    # Utility methods for specific event types
    async def log_user_activity(
        self,
        user_id: int,
        action: str,
        resource_type: str = None,
        resource_id: str = None,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        """Log user activity with GDPR compliance"""
        await self.log_event(
            AuditEventType.API_CALL,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            compliance_standards=[ComplianceStandard.GDPR]
        )
    
    async def log_data_access(
        self,
        user_id: int,
        data_type: str,
        data_id: str,
        operation: str,
        details: Dict[str, Any] = None,
        ip_address: str = None
    ):
        """Log data access with compliance tracking"""
        event_type = {
            "create": AuditEventType.DATA_CREATE,
            "read": AuditEventType.DATA_READ,
            "update": AuditEventType.DATA_UPDATE,
            "delete": AuditEventType.DATA_DELETE,
            "export": AuditEventType.DATA_EXPORT
        }.get(operation, AuditEventType.DATA_READ)
        
        await self.log_event(
            event_type,
            user_id=user_id,
            resource_type=data_type,
            resource_id=data_id,
            action=f"{operation}_{data_type}",
            details=details,
            ip_address=ip_address,
            compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.SOC2]
        )
    
    async def log_security_event(
        self,
        event_type: AuditEventType,
        details: Dict[str, Any],
        user_id: int = None,
        ip_address: str = None,
        severity: str = "warning"
    ):
        """Log security-related events"""
        await self.log_event(
            event_type,
            user_id=user_id,
            action=f"security_{event_type.value}",
            details=details,
            ip_address=ip_address,
            severity=severity,
            compliance_standards=[ComplianceStandard.SOC2]
        )
    
    async def log_file_operation(
        self,
        user_id: int,
        operation: str,
        filename: str,
        file_size: int = None,
        file_type: str = None,
        ip_address: str = None
    ):
        """Log file operations with details"""
        event_type = {
            "upload": AuditEventType.FILE_UPLOAD,
            "download": AuditEventType.FILE_DOWNLOAD,
            "delete": AuditEventType.FILE_DELETE
        }.get(operation, AuditEventType.FILE_UPLOAD)
        
        await self.log_event(
            event_type,
            user_id=user_id,
            resource_type="file",
            resource_id=filename,
            action=f"file_{operation}",
            details={
                "filename": filename,
                "file_size": file_size,
                "file_type": file_type
            },
            ip_address=ip_address,
            compliance_standards=[ComplianceStandard.GDPR, ComplianceStandard.SOC2]
        )


class ComplianceReporter:
    """Generate compliance reports"""
    
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
    
    async def generate_gdpr_report(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate GDPR compliance report"""
        async with get_db_context() as db:
            query = select(AuditLog).where(
                AuditLog.timestamp >= start_date,
                AuditLog.timestamp <= end_date
            )
            
            if user_id:
                query = query.where(AuditLog.user_id == user_id)
            
            result = await db.execute(query)
            audit_logs = result.fetchall()
            
            # Analyze logs for GDPR compliance
            personal_data_access = []
            consent_events = []
            data_exports = []
            
            for log in audit_logs:
                if log.action.startswith("data_read") and self._is_personal_data(log):
                    personal_data_access.append(log)
                elif log.action == "consent_given" or log.action == "consent_withdrawn":
                    consent_events.append(log)
                elif log.action.startswith("data_export"):
                    data_exports.append(log)
            
            return {
                "report_type": "GDPR Compliance Report",
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "user_id": user_id,
                "summary": {
                    "total_events": len(audit_logs),
                    "personal_data_access_events": len(personal_data_access),
                    "consent_events": len(consent_events),
                    "data_export_events": len(data_exports)
                },
                "events": {
                    "personal_data_access": [self._serialize_audit_log(log) for log in personal_data_access],
                    "consent_events": [self._serialize_audit_log(log) for log in consent_events],
                    "data_exports": [self._serialize_audit_log(log) for log in data_exports]
                },
                "compliance_status": "compliant",  # This would be determined by analysis
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def _is_personal_data(self, audit_log: AuditLog) -> bool:
        """Check if audit log involves personal data"""
        personal_data_types = ["user", "document", "audio_file", "transcription"]
        return audit_log.resource_type in personal_data_types
    
    def _serialize_audit_log(self, audit_log: AuditLog) -> Dict[str, Any]:
        """Serialize audit log for reporting"""
        return {
            "id": audit_log.id,
            "timestamp": audit_log.timestamp.isoformat(),
            "user_id": audit_log.user_id,
            "action": audit_log.action,
            "resource_type": audit_log.resource_type,
            "resource_id": audit_log.resource_id,
            "ip_address": audit_log.ip_address,
            "details": audit_log.details
        }


# Global audit logger instance
audit_system = AuditLogger()

__all__ = [
    "AuditLogger",
    "AuditEventType",
    "ComplianceStandard",
    "ComplianceReporter",
    "audit_system"
]