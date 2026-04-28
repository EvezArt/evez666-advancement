#!/usr/bin/env python3
"""Payment Connectivity Validator

Validates connectivity to payment processors before monetization attempts.
Part of self-improvement cycle 10 auto-improvement action.
"""

import requests
import logging
import os
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# Configuration
WORKSPACE_DIR = os.path.expanduser("~/.openclaw/workspace")
LOG_FILE = os.path.expanduser("~/self-improving/payment_validator.log")

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a payment processor connectivity check."""
    processor: str
    passed: bool
    message: str
    details: Optional[Dict] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"


class PaymentValidator:
    """Main validator class for payment processor connectivity."""

    def __init__(self, timeout: int = 10):
        """Initialize validator with timeout for HTTP requests."""
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OpenClaw-PaymentValidator/1.0',
            'Accept': 'application/json'
        })

    def check_kofi_api(self, kofi_username: Optional[str] = None) -> ValidationResult:
        """Check Ko-fi API endpoint connectivity.

        Ko-fi API endpoint: https://api.ko-fi.com/v1/
        Tests basic connectivity without authentication.

        Args:
            kofi_username: Optional Ko-fi username to check specific page

        Returns:
            ValidationResult with pass/fail status
        """
        logger.info("Checking Ko-fi API connectivity...")

        # Test general Ko-fi API availability
        api_url = "https://api.ko-fi.com/v1/"

        try:
            response = self.session.get(api_url, timeout=self.timeout)

            # Ko-fi returns 404 for root, but that's okay - we're testing connectivity
            if response.status_code < 500:
                # If username provided, check specific ko-fi page
                if kofi_username:
                    page_url = f"https://ko-fi.com/{kofi_username}"
                    page_response = self.session.get(page_url, timeout=self.timeout)
                    if page_response.status_code == 200:
                        msg = f"Ko-fi API reachable and page '{kofi_username}' exists"
                        logger.info(msg)
                        return ValidationResult(
                            processor="Ko-fi",
                            passed=True,
                            message=msg,
                            details={
                                "api_status": response.status_code,
                                "page_status": page_response.status_code,
                                "page_url": page_url
                            }
                        )
                    else:
                        msg = f"Ko-fi page '{kofi_username}' returned status {page_response.status_code}"
                        logger.warning(msg)
                        return ValidationResult(
                            processor="Ko-fi",
                            passed=False,
                            message=msg,
                            details={
                                "api_status": response.status_code,
                                "page_status": page_response.status_code
                            }
                        )
                else:
                    msg = "Ko-fi API endpoint reachable"
                    logger.info(msg)
                    return ValidationResult(
                        processor="Ko-fi",
                        passed=True,
                        message=msg,
                        details={"api_status": response.status_code}
                    )
            else:
                msg = f"Ko-fi API returned server error: {response.status_code}"
                logger.error(msg)
                return ValidationResult(
                    processor="Ko-fi",
                    passed=False,
                    message=msg,
                    details={"api_status": response.status_code}
                )

        except requests.exceptions.Timeout:
            msg = "Ko-fi API request timed out"
            logger.error(msg)
            return ValidationResult(
                processor="Ko-fi",
                passed=False,
                message=msg,
                details={"error": "timeout"}
            )
        except requests.exceptions.ConnectionError:
            msg = "Cannot connect to Ko-fi API (network error)"
            logger.error(msg)
            return ValidationResult(
                processor="Ko-fi",
                passed=False,
                message=msg,
                details={"error": "connection_error"}
            )
        except Exception as e:
            msg = f"Unexpected error checking Ko-fi: {str(e)}"
            logger.error(msg)
            return ValidationResult(
                processor="Ko-fi",
                passed=False,
                message=msg,
                details={"error": str(e)}
            )

    def check_paypal_webhook(self, webhook_url: Optional[str] = None,
                            payment_link: Optional[str] = None) -> ValidationResult:
        """Verify PayPal webhook/payment link connectivity.

        Tests PayPal URL accessibility. For webhooks, checks if URL is reachable.
        For payment links, verifies link returns valid response.

        Args:
            webhook_url: Optional PayPal webhook URL to validate
            payment_link: Optional PayPal payment link to validate

        Returns:
            ValidationResult with pass/fail status
        """
        logger.info("Checking PayPal connectivity...")

        results = {}
        issues = []

        # Check payment link if provided
        if payment_link:
            try:
                response = self.session.get(payment_link, timeout=self.timeout, allow_redirects=True)

                # PayPal payment links typically return 200 on success
                if response.status_code in [200, 302, 303]:
                    results["payment_link_status"] = response.status_code
                    logger.info(f"PayPal payment link reachable (status: {response.status_code})")
                else:
                    msg = f"PayPal payment link returned status {response.status_code}"
                    logger.warning(msg)
                    issues.append(msg)
                    results["payment_link_status"] = response.status_code

            except requests.exceptions.Timeout:
                msg = "PayPal payment link request timed out"
                logger.error(msg)
                issues.append(msg)
                results["payment_link_error"] = "timeout"
            except Exception as e:
                msg = f"Error checking PayPal payment link: {str(e)}"
                logger.error(msg)
                issues.append(msg)
                results["payment_link_error"] = str(e)

        # Check webhook URL if provided
        if webhook_url:
            try:
                # PayPal webhooks are typically POST endpoints, but we can test GET for basic connectivity
                response = self.session.get(webhook_url, timeout=self.timeout)

                # Webhook URLs may return 405 (Method Not Allowed) which is okay - proves endpoint exists
                if response.status_code in [200, 405, 401, 403]:
                    results["webhook_status"] = response.status_code
                    logger.info(f"PayPal webhook endpoint reachable (status: {response.status_code})")
                else:
                    msg = f"PayPal webhook returned status {response.status_code}"
                    logger.warning(msg)
                    issues.append(msg)
                    results["webhook_status"] = response.status_code

            except requests.exceptions.Timeout:
                msg = "PayPal webhook request timed out"
                logger.error(msg)
                issues.append(msg)
                results["webhook_error"] = "timeout"
            except Exception as e:
                msg = f"Error checking PayPal webhook: {str(e)}"
                logger.error(msg)
                issues.append(msg)
                results["webhook_error"] = str(e)

        # If neither provided, just test PayPal general connectivity
        if not webhook_url and not payment_link:
            try:
                response = self.session.get("https://www.paypal.com", timeout=self.timeout)
                if response.status_code == 200:
                    msg = "PayPal main site reachable"
                    logger.info(msg)
                    return ValidationResult(
                        processor="PayPal",
                        passed=True,
                        message=msg,
                        details={"paypal_status": response.status_code}
                    )
                else:
                    msg = f"PayPal returned status {response.status_code}"
                    logger.warning(msg)
                    return ValidationResult(
                        processor="PayPal",
                        passed=False,
                        message=msg,
                        details={"paypal_status": response.status_code}
                    )
            except Exception as e:
                msg = f"Cannot connect to PayPal: {str(e)}"
                logger.error(msg)
                return ValidationResult(
                    processor="PayPal",
                    passed=False,
                    message=msg,
                    details={"error": str(e)}
                )

        # Determine overall result
        if issues:
            return ValidationResult(
                processor="PayPal",
                passed=False,
                message="; ".join(issues),
                details=results
            )
        else:
            return ValidationResult(
                processor="PayPal",
                passed=True,
                message="PayPal connectivity validated successfully",
                details=results
            )

    def check_gumroad_product(self, product_url: str) -> ValidationResult:
        """Validate Gumroad product link connectivity.

        Tests if Gumroad product URL is accessible and returns valid product page.

        Args:
            product_url: Gumroad product URL to validate

        Returns:
            ValidationResult with pass/fail status
        """
        logger.info(f"Checking Gumroad product link: {product_url}")

        try:
            response = self.session.get(product_url, timeout=self.timeout, allow_redirects=True)

            # Gumroad product pages typically return 200
            if response.status_code == 200:
                # Check if response contains Gumroad-specific content markers
                content_lower = response.text.lower()
                gumroad_indicators = ['gumroad', 'gumroad.com', 'product', 'buy', 'checkout']

                if any(indicator in content_lower for indicator in gumroad_indicators):
                    msg = f"Gumroad product link valid and accessible: {product_url}"
                    logger.info(msg)
                    return ValidationResult(
                        processor="Gumroad",
                        passed=True,
                        message=msg,
                        details={
                            "url": product_url,
                            "status_code": response.status_code,
                            "final_url": response.url
                        }
                    )
                else:
                    msg = f"URL returned 200 but doesn't appear to be a Gumroad product page: {product_url}"
                    logger.warning(msg)
                    return ValidationResult(
                        processor="Gumroad",
                        passed=False,
                        message=msg,
                        details={
                            "url": product_url,
                            "status_code": response.status_code
                        }
                    )
            elif response.status_code in [301, 302, 303, 307, 308]:
                # Redirect is okay - follows to final destination
                msg = f"Gumroad product URL redirects (status: {response.status_code})"
                logger.info(msg)
                return ValidationResult(
                    processor="Gumroad",
                    passed=True,
                    message=msg,
                    details={
                        "url": product_url,
                        "status_code": response.status_code,
                        "redirect_location": response.headers.get('Location', 'unknown')
                    }
                )
            else:
                msg = f"Gumroad product link returned status {response.status_code}"
                logger.warning(msg)
                return ValidationResult(
                    processor="Gumroad",
                    passed=False,
                    message=msg,
                    details={
                        "url": product_url,
                        "status_code": response.status_code
                    }
                )

        except requests.exceptions.Timeout:
            msg = f"Gumroad product link request timed out: {product_url}"
            logger.error(msg)
            return ValidationResult(
                processor="Gumroad",
                passed=False,
                message=msg,
                details={"url": product_url, "error": "timeout"}
            )
        except requests.exceptions.ConnectionError:
            msg = f"Cannot connect to Gumroad URL: {product_url}"
            logger.error(msg)
            return ValidationResult(
                processor="Gumroad",
                passed=False,
                message=msg,
                details={"url": product_url, "error": "connection_error"}
            )
        except Exception as e:
            msg = f"Unexpected error checking Gumroad product: {str(e)}"
            logger.error(msg)
            return ValidationResult(
                processor="Gumroad",
                passed=False,
                message=msg,
                details={"url": product_url, "error": str(e)}
            )

    def validate_all(self, config: Dict) -> Tuple[bool, List[ValidationResult]]:
        """Run all validation checks based on provided configuration.

        Args:
            config: Dictionary containing payment processor configuration:
                - kofi_username: Ko-fi username (optional)
                - paypal_webhook: PayPal webhook URL (optional)
                - paypal_payment_link: PayPal payment link (optional)
                - gumroad_products: List of Gumroad product URLs (optional)

        Returns:
            Tuple of (overall_pass, list_of_results)
        """
        logger.info("Starting payment connectivity validation...")
        results = []

        # Check Ko-fi
        kofi_username = config.get('kofi_username')
        kofi_result = self.check_kofi_api(kofi_username)
        results.append(kofi_result)

        # Check PayPal
        paypal_webhook = config.get('paypal_webhook')
        paypal_payment_link = config.get('paypal_payment_link')
        paypal_result = self.check_paypal_webhook(paypal_webhook, paypal_payment_link)
        results.append(paypal_result)

        # Check Gumroad products
        gumroad_products = config.get('gumroad_products', [])
        if gumroad_products:
            for product_url in gumroad_products:
                gumroad_result = self.check_gumroad_product(product_url)
                results.append(gumroad_result)
        else:
            logger.info("No Gumroad products configured, skipping")
            results.append(ValidationResult(
                processor="Gumroad",
                passed=True,
                message="No Gumroad products to validate (skipped)",
                details={"skipped": True}
            ))

        # Determine overall pass/fail
        failed = [r for r in results if not r.passed and not r.details.get('skipped')]
        overall_pass = len(failed) == 0

        logger.info(f"Validation complete: {'PASS' if overall_pass else 'FAIL'} "
                   f"({len(failed)} failures out of {len(results)} checks)")

        return overall_pass, results

    def close(self):
        """Clean up session."""
        self.session.close()


def validate_before_monetization(config: Optional[Dict] = None) -> Dict:
    """Integration point: Call this before any revenue generation attempt.

    This function is designed to be called from monetization code paths
    to ensure payment processors are reachable before attempting to
    generate revenue.

    Args:
        config: Optional payment processor configuration. If None, tries to
               load from environment variables or default config file.

    Returns:
        Dictionary with validation results:
        {
            "valid": bool,
            "timestamp": str,
            "results": [
                {"processor": str, "passed": bool, "message": str, "details": dict}
            ],
            "can_proceed": bool  # True if critical validations passed
        }
    """
    logger.info("=" * 60)
    logger.info("PAYMENT CONNECTIVITY VALIDATION - PRE-MONETIZATION CHECK")
    logger.info("=" * 60)

    # Load config if not provided
    if config is None:
        config = _load_config()

    validator = PaymentValidator(timeout=15)

    try:
        overall_pass, results = validator.validate_all(config)

        # Prepare result dictionary
        result_dict = {
            "valid": overall_pass,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "results": [
                {
                    "processor": r.processor,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details or {},
                    "timestamp": r.timestamp
                }
                for r in results
            ],
            "can_proceed": overall_pass  # Could add logic for partial failures
        }

        # Log summary
        logger.info("-" * 60)
        logger.info("VALIDATION SUMMARY:")
        for r in results:
            status = "✓ PASS" if r.passed else "✗ FAIL"
            logger.info(f"  {status}: {r.processor} - {r.message}")
        logger.info("-" * 60)
        logger.info(f"Overall: {'PASS' if overall_pass else 'FAIL'}")

        return result_dict

    finally:
        validator.close()


def _load_config() -> Dict:
    """Load payment processor configuration from environment or defaults.

    Returns:
        Configuration dictionary
    """
    config = {
        'kofi_username': os.environ.get('KOFI_USERNAME'),
        'paypal_webhook': os.environ.get('PAYPAL_WEBHOOK_URL'),
        'paypal_payment_link': os.environ.get('PAYPAL_PAYMENT_LINK'),
        'gumroad_products': []
    }

    # Try to load Gumroad products from environment (comma-separated)
    gumroad_env = os.environ.get('GUMROAD_PRODUCTS')
    if gumroad_env:
        config['gumroad_products'] = [url.strip() for url in gumroad_env.split(',') if url.strip()]

    # Try to load from config file if exists
    config_file = os.path.join(WORKSPACE_DIR, 'payment_config.json')
    if os.path.exists(config_file):
        try:
            import json
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
            logger.info(f"Loaded payment config from {config_file}")
        except Exception as e:
            logger.warning(f"Could not load config file {config_file}: {e}")

    # Log what's being validated
    logger.info("Configuration loaded:")
    logger.info(f"  Ko-fi username: {config.get('kofi_username') or 'Not set'}")
    logger.info(f"  PayPal webhook: {config.get('paypal_webhook') or 'Not set'}")
    logger.info(f"  PayPal payment link: {config.get('paypal_payment_link') or 'Not set'}")
    logger.info(f"  Gumroad products: {len(config.get('gumroad_products', []))} configured")

    return config


if __name__ == "__main__":
    # Run validation as standalone script
    print("Payment Connectivity Validator")
    print("-" * 40)

    result = validate_before_monetization()

    print("\nValidation Results:")
    print(f"  Overall: {'PASS ✓' if result['valid'] else 'FAIL ✗'}")
    print(f"  Can proceed: {'Yes' if result['can_proceed'] else 'No - fix connectivity issues'}")

    print("\nDetailed Results:")
    for r in result['results']:
        status = "✓" if r['passed'] else "✗"
        print(f"  {status} {r['processor']}: {r['message']}")

    print(f"\nLog: {LOG_FILE}")
    print(f"Timestamp: {result['timestamp']}")

    sys.exit(0 if result['valid'] else 1)
