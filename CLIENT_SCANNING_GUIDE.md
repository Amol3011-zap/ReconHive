# ReconHive - Client Website Scanning Guide

**Dashboard URL:** http://localhost:3000  
**API Documentation:** http://localhost:8000/docs  
**Status:** ✅ LIVE & READY

---

## 🎯 QUICK START - SCAN YOUR CLIENT'S WEBSITE

### **Step 1: Open ReconHive Dashboard**

**Navigate to:** http://localhost:3000

You'll see the ReconHive dashboard with:
- Engagements list
- Active scans
- Findings summary
- Reports

### **Step 2: Create New Engagement**

1. Click **"New Engagement"** or **"Create Engagement"**
2. Enter client information:
   - **Client Name:** Your client's company name
   - **Engagement ID:** Unique identifier
   - **Scope:** The websites/domains to test
   - **Start Date:** Today's date
   - **End Date:** Assessment completion date

### **Step 3: Add Target Domain/URL**

In the engagement, add your target:

**Examples of valid targets:**
- `example.com` (will scan entire domain)
- `subdomain.example.com` (specific subdomain)
- `https://example.com` (with protocol)
- `192.168.1.1` (IP address)
- Multiple domains (separated by commas)

### **Step 4: Start Reconnaissance Scan**

Click **"Start Reconnaissance"** button

The system will:
1. ✅ Execute 11 reconnaissance phases
2. ✅ Discover subdomains
3. ✅ Identify technologies
4. ✅ Find endpoints
5. ✅ Detect potential vulnerabilities
6. ✅ Generate findings

### **Step 5: Monitor Scan Progress**

Real-time progress shows:
- Current phase (1-11)
- Execution time
- Assets discovered
- Findings identified

### **Step 6: Review Findings**

Once scan completes:

1. Click **"View Findings"**
2. Review discovered vulnerabilities:
   - **SQL Injection** (if detected)
   - **XSS** (if detected)
   - **SSRF** (if detected)
   - Misconfigurations
   - Technology details

### **Step 7: Validate Critical Findings**

For each finding, ReconHive automatically:
- ✅ Tests vulnerability existence
- ✅ Captures evidence (screenshots, responses)
- ✅ Scores confidence level (0.0-1.0)
- ✅ Maps to OWASP category
- ✅ Provides remediation guidance

### **Step 8: Generate Client Report**

Click **"Generate Report"**

Report includes:
- Executive summary
- Attack surface analysis
- Detailed findings with evidence
- Severity breakdown
- Remediation recommendations
- Timeline

---

## 🔍 WHAT GETS SCANNED

### **Phase 1: Asset Discovery**
- Subdomains
- ASN information
- IP addresses
- Historical records

### **Phase 2: URL Collection**
- Web endpoints
- Archived URLs
- API paths
- Hidden pages

### **Phase 3: DNS Analysis**
- DNS records (A, AAAA, CNAME, MX, etc.)
- Wildcard detection
- Takeover candidates
- DNSSEC validation

### **Phase 4: Web Discovery**
- Alive hosts
- Screenshots
- Redirects
- Response headers
- Technology fingerprints

### **Phase 5: Technology Detection**
- Web servers (Apache, Nginx, IIS, Tomcat)
- Frameworks (React, Angular, Vue, Django, Flask)
- CMS (WordPress, Drupal, Joomla)
- Databases
- CDN/WAF detection

### **Phase 6: JavaScript Analysis**
- Extracted endpoints
- API discovery
- GraphQL endpoints
- WebSocket connections
- Potential secrets exposure

### **Phase 7: API Discovery**
- REST endpoints
- GraphQL introspection
- API documentation
- SOAP/XML-RPC endpoints
- gRPC services

### **Phase 8: Parameter Discovery**
- Hidden query parameters
- POST body parameters
- Custom headers
- Form fields

### **Phase 9: Content Discovery**
- Hidden directories
- Backup files
- Admin panels
- Configuration files
- Sensitive files (.git, .env, etc.)

### **Phase 10: Network Discovery**
- Open ports
- Running services
- Service versions
- Banner information
- Network topology

### **Phase 11: Validation**
- SQL Injection detection
- XSS detection
- SSRF detection
- Security header analysis
- SSL/TLS configuration
- Outdated software detection

---

## 🛡️ VULNERABILITY VALIDATION

### **Automatic Validation for:**

**SQL Injection:**
```
- Error-based SQLi (SQL error messages)
- Boolean-based blind SQLi (response differences)
- Time-based blind SQLi (timing analysis)
- Union-based SQLi (column enumeration)
```

**Cross-Site Scripting (XSS):**
```
- Reflected XSS (payload echoed in response)
- Stored XSS (payload persisted)
- DOM XSS (JavaScript execution)
- Context-specific payloads
```

**Server-Side Request Forgery (SSRF):**
```
- Localhost/127.0.0.1 access
- Cloud metadata endpoint access (AWS, GCP, Azure)
- Internal service detection
- Timing-based detection
```

**Other Checks:**
```
- Security header analysis (CSP, HSTS, etc.)
- SSL/TLS configuration
- Directory listing enabled
- Sensitive file exposure
- Technology version detection
- API misconfiguration
- Weak authentication
```

---

## 📊 FINDINGS BREAKDOWN

### **Severity Levels**

| Level | CVSS | Examples |
|-------|------|----------|
| **Critical** | 9.0-10.0 | RCE, Auth Bypass, Complete Takeover |
| **High** | 7.0-8.9 | IDOR, Privilege Escalation, Data Breach |
| **Medium** | 4.0-6.9 | Weak Controls, Misconfig, Logic Flaws |
| **Low** | 0.1-3.9 | Best Practice Violations |
| **Info** | - | Inventory, Tech Stack |

### **Example Report Structure**

For each finding:
1. **Title:** Clear vulnerability name
2. **Severity:** Critical/High/Medium/Low
3. **Affected Asset:** URL or endpoint
4. **Description:** What was found
5. **Evidence:** Screenshots, response examples
6. **Impact:** Business consequence
7. **Remediation:** Step-by-step fix
8. **OWASP:** Category mapping (A03, A01, etc.)
9. **Confidence:** 0.0-1.0 score

---

## 🎬 EXAMPLE SCAN WORKFLOW

### **Scenario: Scan acme.com**

```
1. Dashboard → New Engagement
   Client: ACME Corporation
   Domain: acme.com
   
2. Start Reconnaissance
   
3. Monitor Progress
   Phase 1: Asset Discovery → Found 24 subdomains
   Phase 2: URL Collection → Found 156 endpoints
   Phase 3: DNS Analysis → Resolved IPs
   Phase 4: Web Discovery → 12 live hosts
   Phase 5: Technology Detection → Django, PostgreSQL, Nginx
   Phase 6: JavaScript Analysis → 3 API endpoints discovered
   Phase 7: API Discovery → REST API at /api/v1
   Phase 8: Parameter Discovery → 8 hidden parameters
   Phase 9: Content Discovery → Admin panel found
   Phase 10: Network Discovery → 5 open ports
   Phase 11: Validation → Potential SQL injection
   
4. Review Findings
   ✅ SQL Injection: Confirmed (95% confidence)
   ✅ Missing Security Headers: Confirmed
   ✅ Outdated Django Version: Detected
   ⚠️  Exposed API Documentation: Found
   
5. Generate Report
   - Executive summary
   - 12 findings total (1 Critical, 3 High, 5 Medium, 3 Low)
   - Attack surface map
   - Remediation roadmap
```

---

## 📈 DASHBOARD FEATURES

### **Engagements Tab**
- List all client assessments
- Filter by status, date, severity
- Export reports
- Schedule recurring scans

### **Findings Tab**
- View all vulnerabilities
- Filter by severity, type, asset
- Validate findings
- Mark as remediated
- Track resolution time

### **Reports Tab**
- Generate executive summaries
- Download as PDF/DOCX
- Email to stakeholders
- Share with client
- Track version history

### **Assets Tab**
- Technology inventory
- Subdomain list
- Endpoint catalog
- Port inventory
- API documentation

### **Agents Tab**
- Monitor running agents
- View agent capabilities
- Check execution logs
- See statistics

---

## 🔒 AUTHORIZATION & COMPLIANCE

✅ **All Testing is Non-Exploitative:**
- Tests vulnerability existence (no exploitation)
- Captures evidence (screenshots, responses)
- No data exfiltration
- No system modification
- Read-only proof-of-concept
- Full audit trail

✅ **Compliance Features:**
- Authorization enforcement
- Scope validation
- Execution logging
- Finding tracking
- Report generation
- Evidence preservation

---

## 💡 PRO TIPS FOR CLIENT SCANNING

### **Before Scanning:**
1. ✅ Get written authorization
2. ✅ Define scope clearly (domains, IPs, excluded systems)
3. ✅ Schedule during maintenance window if possible
4. ✅ Notify client's technical team
5. ✅ Set expectations (scan duration: 15-60 minutes)

### **During Scanning:**
1. ✅ Monitor real-time progress dashboard
2. ✅ Check for false positives
3. ✅ Review findings as they appear
4. ✅ Validate critical findings manually

### **After Scanning:**
1. ✅ Review all findings with team
2. ✅ Validate confidence scores
3. ✅ Prepare remediation roadmap
4. ✅ Generate professional report
5. ✅ Schedule follow-up assessment
6. ✅ Track remediation progress

### **Report Best Practices:**
1. ✅ Executive summary first (non-technical)
2. ✅ Show evidence (not claims)
3. ✅ Prioritize by severity
4. ✅ Provide specific remediation steps
5. ✅ Include timeline for fixes
6. ✅ Offer follow-up testing

---

## 🚨 COMMON FINDINGS EXPLAINED

### **SQL Injection (Critical)**
**What it means:** Attacker can execute arbitrary SQL commands  
**Risk:** Database breach, data theft, system compromise  
**Fix:** Use parameterized queries, input validation  
**Timeline:** Fix immediately

### **XSS (High)**
**What it means:** Attacker can inject JavaScript into user browsers  
**Risk:** Session hijacking, credential theft, malware distribution  
**Fix:** HTML encoding, Content Security Policy (CSP)  
**Timeline:** Fix within 1 week

### **Missing Security Headers (Medium)**
**What it means:** Browser security protections not enabled  
**Risk:** MIME sniffing, clickjacking, XSS attacks  
**Fix:** Add CSP, X-Frame-Options, X-Content-Type-Options  
**Timeline:** Fix within 2 weeks

### **Outdated Software (High)**
**What it means:** Running vulnerable version of framework/library  
**Risk:** Known exploits may be available  
**Fix:** Update to latest patched version  
**Timeline:** Fix within 1-2 weeks

---

## 📞 SUPPORT & DOCUMENTATION

**Dashboard:** http://localhost:3000  
**API Docs:** http://localhost:8000/docs  
**Database Admin:** http://localhost:5050  

**Additional Guides:**
- QUICK_START.md
- TESTING_GUIDE.md
- VALIDATION_ENGINE_SUMMARY.md

---

## ✅ READY TO SCAN

Your ReconHive instance is fully operational and ready for client website assessments.

**Next Steps:**
1. Open http://localhost:3000
2. Create new engagement
3. Add client website
4. Start reconnaissance
5. Review findings
6. Generate report
7. Deliver to client

**All 11 reconnaissance phases, 183+ security payloads, and 3 core validators are active and ready!**

