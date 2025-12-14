# Test Log Files for Cybersecurity Multi-Agent System

This directory contains sample log files for testing the cybersecurity monitoring system.

## Log Files

### 1. `auth.log`
**Purpose**: Authentication and SSH login attempts

**Contains**:
- ✅ Successful logins
- ✅ Failed password attempts (brute force patterns)
- ✅ Authentication failures
- ✅ Invalid login attempts
- ✅ Privilege escalation events

**Attack Patterns**:
- Multiple failed login attempts from same IP (brute force)
- Repeated authentication failures

**Expected Detections**:
- Brute force attacks (rate limiting)
- Authentication failures

---

### 2. `web_access.log`
**Purpose**: HTTP web server access logs

**Contains**:
- ✅ Normal web requests
- ✅ SQL injection attempts
- ✅ XSS (Cross-Site Scripting) attempts
- ✅ Path traversal attempts
- ✅ Directory enumeration
- ✅ Rate limiting violations

**Attack Patterns**:
- SQL injection: `' OR '1'='1`, `UNION SELECT`, `DROP TABLE`
- XSS: `<script>`, `javascript:`, `onerror=`
- Path traversal: `../../etc/passwd`, `..\\..\\windows\\system32`

**Expected Detections**:
- SQL injection attacks
- XSS attempts
- Path traversal attempts
- Rate limiting (multiple requests from same IP)

---

### 3. `application.log`
**Purpose**: Application-level events and errors

**Contains**:
- ✅ Application startup/shutdown
- ✅ Login attempts
- ✅ SQL injection attempts
- ✅ XSS attempts
- ✅ Path traversal attempts
- ✅ Database connections
- ✅ API requests

**Attack Patterns**:
- SQL injection in application logs
- XSS in application logs
- Path traversal in application logs

**Expected Detections**:
- SQL injection
- XSS attempts
- Path traversal
- Authentication failures

---

### 4. `system.log`
**Purpose**: System-level events

**Contains**:
- ✅ System service events
- ✅ SSH login attempts
- ✅ Firewall blocks
- ✅ Kernel events
- ✅ Service starts/stops

**Attack Patterns**:
- Multiple failed SSH attempts
- Firewall blocks (suspicious IPs)

**Expected Detections**:
- Brute force attacks
- Suspicious IP addresses

---

### 5. `security.log`
**Purpose**: Security-specific events

**Contains**:
- ✅ Login successes/failures
- ✅ Brute force detections
- ✅ SQL injection attempts
- ✅ XSS attempts
- ✅ Path traversal attempts
- ✅ Rate limiting events
- ✅ Privilege escalations
- ✅ Access denials

**Attack Patterns**:
- All major attack types
- Security event classifications

**Expected Detections**:
- All attack types
- Security event correlation

---

## How to Use

### Option 1: Upload via Streamlit UI

1. Go to the **Analysis** tab
2. Select **File Upload** for log entries
3. Upload any of the log files
4. Click **Run Security Analysis**

### Option 2: Use in Code

```python
from coordinator_langgraph import LangGraphCoordinator

coordinator = LangGraphCoordinator({})

# Read log file
with open('test_logs/auth.log', 'r') as f:
    log_entries = [line.strip() for line in f if line.strip()]

# Process logs
result = coordinator.process_security_event(
    log_entries=log_entries
)

# View alerts
for alert in result.get('log_alerts', []):
    print(f"{alert['severity']}: {alert['description']}")
```

### Option 3: Combine Multiple Log Files

```python
import glob

log_files = glob.glob('test_logs/*.log')
all_logs = []

for log_file in log_files:
    with open(log_file, 'r') as f:
        all_logs.extend([line.strip() for line in f if line.strip()])

# Process all logs
result = coordinator.process_security_event(
    log_entries=all_logs
)
```

---

## Expected Detections

### Brute Force Attacks
- **File**: `auth.log`, `application.log`, `system.log`, `security.log`
- **Pattern**: Multiple "Failed password" or "authentication failure" entries
- **Expected Alert**: `brute_force_detected` (HIGH severity)

### SQL Injection
- **File**: `web_access.log`, `application.log`, `security.log`
- **Pattern**: `' OR '1'='1`, `UNION SELECT`, `DROP TABLE`
- **Expected Alert**: `log_sql_injection` (HIGH severity)

### XSS Attempts
- **File**: `web_access.log`, `application.log`, `security.log`
- **Pattern**: `<script>`, `javascript:`, `onerror=`
- **Expected Alert**: `log_xss_attempt` (MEDIUM severity)

### Path Traversal
- **File**: `web_access.log`, `application.log`, `security.log`
- **Pattern**: `../../etc/passwd`, `..\\..\\windows\\system32`
- **Expected Alert**: `log_path_traversal` (MEDIUM severity)

---

## Test Scenarios

### Scenario 1: Brute Force Detection
**Use**: `auth.log`
**Expected**: Multiple alerts for brute force attacks from IPs 192.168.1.100, 198.51.100.25

### Scenario 2: SQL Injection
**Use**: `web_access.log`
**Expected**: Alerts for SQL injection patterns in URLs

### Scenario 3: XSS Attempts
**Use**: `web_access.log` or `application.log`
**Expected**: Alerts for XSS patterns in requests

### Scenario 4: Path Traversal
**Use**: `web_access.log` or `application.log`
**Expected**: Alerts for path traversal attempts

### Scenario 5: Comprehensive Test
**Use**: All log files combined
**Expected**: Multiple alerts across all attack types

---

## Log Format Notes

- **Auth logs**: Standard Linux auth.log format
- **Web access logs**: Apache/Nginx combined log format
- **Application logs**: Custom format with timestamps and log levels
- **System logs**: Systemd/journald format
- **Security logs**: Custom security event format

---

## Tips

1. **Start Simple**: Test with one log file first (`auth.log` or `security.log`)
2. **Check Alerts**: Verify that expected attack patterns are detected
3. **Combine Logs**: Test with multiple log files for comprehensive analysis
4. **Verify Severity**: Check that alerts have appropriate severity levels
5. **Check Rate Limiting**: Verify that brute force attacks trigger rate limit alerts

---

## File Locations

All test log files are in the `test_logs/` directory:

```
test_logs/
├── auth.log          # Authentication logs
├── web_access.log    # Web server access logs
├── application.log   # Application logs
├── system.log        # System logs
├── security.log      # Security event logs
└── README.md         # This file
```

---

**Ready to test!** Upload any log file through the Streamlit UI or use them programmatically. 🚀
