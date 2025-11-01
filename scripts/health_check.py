#!/usr/bin/env python3
"""
Comprehensive Health Check Script for Odoo Blue-Green Deployment

This script validates Odoo environment health across multiple dimensions:
- Basic liveness (HTTP response)
- Database connectivity and query performance
- Odoo server responsiveness and module loading
- Critical workflow smoke tests
- Performance metrics validation

Exit codes:
  0: All checks passed (healthy)
  1: Health check failed (unhealthy)
  2: Configuration error or invalid arguments
"""

import argparse
import json
import sys
import time
from typing import Dict, List, Tuple
from urllib.error import URLError
from urllib.request import Request, urlopen
import socket
import xmlrpc.client

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


class HealthChecker:
    """Comprehensive health check for Odoo environments"""

    def __init__(self, base_url: str, db_name: str = "postgres",
                 username: str = "admin", password: str = "admin",
                 timeout: int = 30, comprehensive: bool = False):
        self.base_url = base_url.rstrip('/')
        self.db_name = db_name
        self.username = username
        self.password = password
        self.timeout = timeout
        self.comprehensive = comprehensive
        self.results = {
            'status': 'healthy',
            'checks': {},
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'metadata': {
                'base_url': base_url,
                'database': db_name,
                'comprehensive': comprehensive
            }
        }

    def run_all_checks(self) -> Dict:
        """Run all health checks and return results"""
        print(f"{Colors.BLUE}🏥 Running health checks on {self.base_url}...{Colors.RESET}\n")

        # Basic checks (always run)
        self._check_http_connectivity()
        self._check_basic_health_endpoint()
        self._check_database_connectivity()
        self._check_odoo_responsiveness()

        # Comprehensive checks (optional)
        if self.comprehensive:
            print(f"\n{Colors.BLUE}📋 Running comprehensive checks...{Colors.RESET}\n")
            self._check_module_loading()
            self._check_filestore_access()
            self._check_response_time()
            self._check_critical_workflows()

        # Print summary
        self._print_summary()

        return self.results

    def _check_http_connectivity(self):
        """Check 1: Basic HTTP connectivity"""
        check_name = "http_connectivity"
        print(f"  → Checking HTTP connectivity...")

        try:
            # Parse URL to get host and port
            from urllib.parse import urlparse
            parsed = urlparse(self.base_url)
            host = parsed.hostname or 'localhost'
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)

            # Try TCP connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                self.results['checks'][check_name] = {
                    'status': 'healthy',
                    'message': f'TCP connection successful to {host}:{port}'
                }
                print(f"    {Colors.GREEN}✓ TCP connection successful{Colors.RESET}")
            else:
                self._mark_unhealthy(check_name, f'Cannot connect to {host}:{port}')
                print(f"    {Colors.RED}✗ TCP connection failed{Colors.RESET}")

        except Exception as e:
            self._mark_unhealthy(check_name, str(e))
            print(f"    {Colors.RED}✗ Connectivity check failed: {e}{Colors.RESET}")

    def _check_basic_health_endpoint(self):
        """Check 2: Basic health endpoint (/web/health)"""
        check_name = "health_endpoint"
        print(f"  → Checking /web/health endpoint...")

        try:
            url = f"{self.base_url}/web/health"
            req = Request(url)
            req.add_header('User-Agent', 'HealthChecker/1.0')

            with urlopen(req, timeout=self.timeout) as response:
                status_code = response.getcode()
                content = response.read().decode('utf-8')

                if status_code == 200:
                    self.results['checks'][check_name] = {
                        'status': 'healthy',
                        'message': 'Health endpoint responding',
                        'http_status': status_code,
                        'response': content.strip()
                    }
                    print(f"    {Colors.GREEN}✓ Health endpoint OK (200){Colors.RESET}")
                else:
                    self._mark_unhealthy(check_name, f'HTTP {status_code}: {content}')
                    print(f"    {Colors.RED}✗ Health endpoint returned {status_code}{Colors.RESET}")

        except URLError as e:
            self._mark_unhealthy(check_name, f'URLError: {e.reason}')
            print(f"    {Colors.RED}✗ Health endpoint unreachable: {e.reason}{Colors.RESET}")
        except Exception as e:
            self._mark_unhealthy(check_name, str(e))
            print(f"    {Colors.RED}✗ Health endpoint check failed: {e}{Colors.RESET}")

    def _check_database_connectivity(self):
        """Check 3: Database connectivity via XML-RPC"""
        check_name = "database_connectivity"
        print(f"  → Checking database connectivity...")

        try:
            # Test database list endpoint (doesn't require auth)
            db_list_url = f"{self.base_url}/xmlrpc/2/db"
            db_proxy = xmlrpc.client.ServerProxy(db_list_url, allow_none=True)

            # List databases (with timeout)
            socket.setdefaulttimeout(self.timeout)
            databases = db_proxy.list()

            if self.db_name in databases:
                self.results['checks'][check_name] = {
                    'status': 'healthy',
                    'message': f'Database {self.db_name} accessible',
                    'databases': databases
                }
                print(f"    {Colors.GREEN}✓ Database {self.db_name} accessible{Colors.RESET}")
            else:
                self._mark_unhealthy(check_name,
                                     f'Database {self.db_name} not found. Available: {databases}')
                print(f"    {Colors.RED}✗ Database {self.db_name} not found{Colors.RESET}")

        except Exception as e:
            self._mark_unhealthy(check_name, f'Database connectivity failed: {str(e)}')
            print(f"    {Colors.RED}✗ Database connectivity failed: {e}{Colors.RESET}")
        finally:
            socket.setdefaulttimeout(None)

    def _check_odoo_responsiveness(self):
        """Check 4: Odoo server responsiveness (authentication test)"""
        check_name = "odoo_responsiveness"
        print(f"  → Checking Odoo server responsiveness...")

        try:
            common_url = f"{self.base_url}/xmlrpc/2/common"
            common = xmlrpc.client.ServerProxy(common_url, allow_none=True)

            # Test authentication
            socket.setdefaulttimeout(self.timeout)
            start_time = time.time()
            uid = common.authenticate(self.db_name, self.username, self.password, {})
            auth_time = time.time() - start_time

            if uid:
                self.results['checks'][check_name] = {
                    'status': 'healthy',
                    'message': 'Authentication successful',
                    'user_id': uid,
                    'auth_time_seconds': round(auth_time, 3)
                }
                print(f"    {Colors.GREEN}✓ Authentication successful (uid={uid}, {auth_time:.3f}s){Colors.RESET}")
            else:
                self._mark_unhealthy(check_name, 'Authentication failed (invalid credentials)')
                print(f"    {Colors.RED}✗ Authentication failed{Colors.RESET}")

        except Exception as e:
            self._mark_unhealthy(check_name, f'Odoo server not responding: {str(e)}')
            print(f"    {Colors.RED}✗ Odoo server not responding: {e}{Colors.RESET}")
        finally:
            socket.setdefaulttimeout(None)

    def _check_module_loading(self):
        """Check 5: Verify all modules loaded successfully"""
        check_name = "module_loading"
        print(f"  → Checking module loading status...")

        try:
            # Authenticate
            common = xmlrpc.client.ServerProxy(f"{self.base_url}/xmlrpc/2/common")
            uid = common.authenticate(self.db_name, self.username, self.password, {})

            if not uid:
                self._mark_unhealthy(check_name, 'Authentication failed')
                return

            # Get module status
            models = xmlrpc.client.ServerProxy(f"{self.base_url}/xmlrpc/2/object")
            socket.setdefaulttimeout(self.timeout)

            installed_modules = models.execute_kw(
                self.db_name, uid, self.password,
                'ir.module.module', 'search_read',
                [[('state', '=', 'installed')]],
                {'fields': ['name', 'state']}
            )

            to_upgrade_modules = models.execute_kw(
                self.db_name, uid, self.password,
                'ir.module.module', 'search_count',
                [[('state', '=', 'to upgrade')]]
            )

            to_install_modules = models.execute_kw(
                self.db_name, uid, self.password,
                'ir.module.module', 'search_count',
                [[('state', '=', 'to install')]]
            )

            if to_upgrade_modules > 0 or to_install_modules > 0:
                self._mark_unhealthy(check_name,
                                     f'{to_upgrade_modules} modules to upgrade, {to_install_modules} to install')
                print(f"    {Colors.YELLOW}⚠ Pending module operations detected{Colors.RESET}")
            else:
                self.results['checks'][check_name] = {
                    'status': 'healthy',
                    'message': f'{len(installed_modules)} modules installed',
                    'installed_count': len(installed_modules)
                }
                print(f"    {Colors.GREEN}✓ All modules loaded ({len(installed_modules)} installed){Colors.RESET}")

        except Exception as e:
            self._mark_unhealthy(check_name, f'Module check failed: {str(e)}')
            print(f"    {Colors.RED}✗ Module check failed: {e}{Colors.RESET}")
        finally:
            socket.setdefaulttimeout(None)

    def _check_filestore_access(self):
        """Check 6: Verify filestore is accessible"""
        check_name = "filestore_access"
        print(f"  → Checking filestore access...")

        try:
            # Authenticate
            common = xmlrpc.client.ServerProxy(f"{self.base_url}/xmlrpc/2/common")
            uid = common.authenticate(self.db_name, self.username, self.password, {})

            if not uid:
                self._mark_unhealthy(check_name, 'Authentication failed')
                return

            # Check attachments (filestore proxy)
            models = xmlrpc.client.ServerProxy(f"{self.base_url}/xmlrpc/2/object")
            socket.setdefaulttimeout(self.timeout)

            attachment_count = models.execute_kw(
                self.db_name, uid, self.password,
                'ir.attachment', 'search_count',
                [[('type', '=', 'binary')]]
            )

            self.results['checks'][check_name] = {
                'status': 'healthy',
                'message': f'Filestore accessible ({attachment_count} binary attachments)',
                'attachment_count': attachment_count
            }
            print(f"    {Colors.GREEN}✓ Filestore accessible ({attachment_count} attachments){Colors.RESET}")

        except Exception as e:
            self._mark_unhealthy(check_name, f'Filestore check failed: {str(e)}')
            print(f"    {Colors.RED}✗ Filestore check failed: {e}{Colors.RESET}")
        finally:
            socket.setdefaulttimeout(None)

    def _check_response_time(self):
        """Check 7: Measure and validate response time"""
        check_name = "response_time"
        print(f"  → Measuring response time...")

        try:
            # Sample 5 requests to /web/health
            response_times = []
            for i in range(5):
                start_time = time.time()
                req = Request(f"{self.base_url}/web/health")
                with urlopen(req, timeout=self.timeout) as response:
                    response.read()
                response_times.append(time.time() - start_time)

            avg_response_time = sum(response_times) / len(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]

            # Threshold: P95 should be under 500ms
            if p95_response_time < 0.5:
                self.results['checks'][check_name] = {
                    'status': 'healthy',
                    'message': 'Response time within SLA',
                    'avg_ms': round(avg_response_time * 1000, 2),
                    'p95_ms': round(p95_response_time * 1000, 2)
                }
                print(f"    {Colors.GREEN}✓ Response time OK (avg={avg_response_time*1000:.0f}ms, p95={p95_response_time*1000:.0f}ms){Colors.RESET}")
            else:
                self._mark_unhealthy(check_name,
                                     f'Response time too high (p95={p95_response_time*1000:.0f}ms)')
                print(f"    {Colors.YELLOW}⚠ Response time high (p95={p95_response_time*1000:.0f}ms){Colors.RESET}")

        except Exception as e:
            self._mark_unhealthy(check_name, f'Response time check failed: {str(e)}')
            print(f"    {Colors.RED}✗ Response time check failed: {e}{Colors.RESET}")

    def _check_critical_workflows(self):
        """Check 8: Critical workflow smoke tests"""
        check_name = "critical_workflows"
        print(f"  → Running critical workflow smoke tests...")

        try:
            # Authenticate
            common = xmlrpc.client.ServerProxy(f"{self.base_url}/xmlrpc/2/common")
            uid = common.authenticate(self.db_name, self.username, self.password, {})

            if not uid:
                self._mark_unhealthy(check_name, 'Authentication failed')
                return

            models = xmlrpc.client.ServerProxy(f"{self.base_url}/xmlrpc/2/object")
            socket.setdefaulttimeout(self.timeout)

            # Test 1: Create partner record
            partner_id = models.execute_kw(
                self.db_name, uid, self.password,
                'res.partner', 'create',
                [{'name': 'Health Check Test Partner',
                  'email': 'healthcheck@example.com'}]
            )

            # Test 2: Search for created record
            found_partners = models.execute_kw(
                self.db_name, uid, self.password,
                'res.partner', 'search',
                [[('id', '=', partner_id)]]
            )

            # Test 3: Update record
            models.execute_kw(
                self.db_name, uid, self.password,
                'res.partner', 'write',
                [[partner_id], {'phone': '+1234567890'}]
            )

            # Test 4: Delete record (cleanup)
            models.execute_kw(
                self.db_name, uid, self.password,
                'res.partner', 'unlink',
                [[partner_id]]
            )

            if partner_id and found_partners:
                self.results['checks'][check_name] = {
                    'status': 'healthy',
                    'message': 'CRUD operations successful',
                    'tests_passed': ['create', 'read', 'update', 'delete']
                }
                print(f"    {Colors.GREEN}✓ Critical workflows OK (CRUD operations successful){Colors.RESET}")
            else:
                self._mark_unhealthy(check_name, 'CRUD operations failed')
                print(f"    {Colors.RED}✗ CRUD operations failed{Colors.RESET}")

        except Exception as e:
            self._mark_unhealthy(check_name, f'Workflow tests failed: {str(e)}')
            print(f"    {Colors.RED}✗ Workflow tests failed: {e}{Colors.RESET}")
        finally:
            socket.setdefaulttimeout(None)

    def _mark_unhealthy(self, check_name: str, message: str):
        """Mark a check as unhealthy and update overall status"""
        self.results['status'] = 'unhealthy'
        self.results['checks'][check_name] = {
            'status': 'unhealthy',
            'message': message
        }

    def _print_summary(self):
        """Print health check summary"""
        print(f"\n{'='*60}")
        print(f"{Colors.BLUE}Health Check Summary{Colors.RESET}")
        print(f"{'='*60}")

        total_checks = len(self.results['checks'])
        healthy_checks = sum(1 for c in self.results['checks'].values()
                             if c.get('status') == 'healthy')
        unhealthy_checks = total_checks - healthy_checks

        if self.results['status'] == 'healthy':
            status_color = Colors.GREEN
            status_icon = '✓'
        else:
            status_color = Colors.RED
            status_icon = '✗'

        print(f"Overall Status: {status_color}{status_icon} {self.results['status'].upper()}{Colors.RESET}")
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {Colors.GREEN}{healthy_checks}{Colors.RESET}")
        print(f"Failed: {Colors.RED}{unhealthy_checks}{Colors.RESET}")
        print(f"{'='*60}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Comprehensive health check for Odoo blue-green deployment',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--url', type=str, default='http://localhost:8069',
                        help='Odoo base URL (default: http://localhost:8069)')
    parser.add_argument('--target', type=str, choices=['blue', 'green'],
                        help='Deployment target (blue=8069, green=9069)')
    parser.add_argument('--db', type=str, default='postgres',
                        help='Database name (default: postgres)')
    parser.add_argument('--username', type=str, default='admin',
                        help='Username for authentication (default: admin)')
    parser.add_argument('--password', type=str, default='admin',
                        help='Password for authentication (default: admin)')
    parser.add_argument('--timeout', type=int, default=30,
                        help='Request timeout in seconds (default: 30)')
    parser.add_argument('--comprehensive', action='store_true',
                        help='Run comprehensive health checks (slower)')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')

    args = parser.parse_args()

    # Auto-detect URL from target
    if args.target:
        if args.target == 'blue':
            args.url = 'http://localhost:8069'
        elif args.target == 'green':
            args.url = 'http://localhost:9069'

    # Run health checks
    checker = HealthChecker(
        base_url=args.url,
        db_name=args.db,
        username=args.username,
        password=args.password,
        timeout=args.timeout,
        comprehensive=args.comprehensive
    )

    results = checker.run_all_checks()

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))

    # Exit with appropriate code
    if results['status'] == 'healthy':
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
