"""Decorators for safety checks, authentication, and audit logging."""

from functools import wraps
from typing import List, Callable, Any
import time


def requires_role(*roles: str):
    """Decorator to enforce role-based access control.

    Args:
        *roles: Required roles for the function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get current user from kwargs or context
            current_user = kwargs.get('current_user')
            context = kwargs.get('_context', {})

            if not current_user and context:
                current_user = context.get('current_user')

            if not current_user:
                return {
                    "error": "Authentication required",
                    "code": "AUTH_REQUIRED"
                }

            # Get user roles from context
            user_roles = context.get('user_roles', {}).get(current_user, [])

            # Check if user has required role
            if not any(role in user_roles for role in roles):
                return {
                    "error": f"Unauthorized: requires one of {roles}",
                    "code": "UNAUTHORIZED",
                    "required_roles": roles,
                    "user_roles": user_roles
                }

            return func(*args, **kwargs)

        wrapper._required_roles = roles
        return wrapper
    return decorator


def requires_authentication(func: Callable) -> Callable:
    """Decorator to require authentication before function execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        context = kwargs.get('_context', {})
        current_user = kwargs.get('current_user')

        if not current_user:
            current_user = context.get('current_user')

        if not current_user:
            return {
                "error": "Authentication required",
                "code": "AUTH_REQUIRED"
            }

        # Check if user is authenticated
        authenticated_users = context.get('authenticated_users', set())
        if current_user not in authenticated_users:
            return {
                "error": "User not authenticated",
                "code": "NOT_AUTHENTICATED",
                "user": current_user
            }

        return func(*args, **kwargs)

    wrapper._requires_auth = True
    return wrapper


def audit_log(func: Callable) -> Callable:
    """Decorator to log function calls for audit trail."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        context = kwargs.get('_context', {})
        audit_trail = context.get('audit_trail', [])

        # Record function call
        audit_entry = {
            'timestamp': time.time(),
            'function': func.__name__,
            'user': kwargs.get('current_user', context.get('current_user', 'unknown')),
            'args': {k: v for k, v in kwargs.items() if k not in ['_context', 'current_user']},
        }

        try:
            result = func(*args, **kwargs)
            audit_entry['success'] = not isinstance(result, dict) or 'error' not in result
            audit_entry['result_summary'] = str(result)[:200] if result else None
        except Exception as e:
            audit_entry['success'] = False
            audit_entry['error'] = str(e)
            raise
        finally:
            audit_trail.append(audit_entry)

        return result

    wrapper._audit_logged = True
    return wrapper


def safety_check(*checks: str):
    """Decorator to enforce safety checks before function execution.

    Args:
        *checks: Names of safety checks to perform (e.g., 'allergy_check', 'interaction_check')
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            context = kwargs.get('_context', {})
            safety_monitor = context.get('safety_monitor')

            if safety_monitor:
                # Perform safety checks
                for check in checks:
                    check_result = safety_monitor.perform_check(check, kwargs)
                    if not check_result.get('passed', True):
                        return {
                            "error": f"Safety check failed: {check}",
                            "code": "SAFETY_CHECK_FAILED",
                            "check": check,
                            "details": check_result.get('details', '')
                        }

            return func(*args, **kwargs)

        wrapper._safety_checks = checks
        return wrapper
    return decorator


def rate_limit(max_calls: int, period: float):
    """Decorator to rate limit function calls.

    Args:
        max_calls: Maximum number of calls allowed
        period: Time period in seconds
    """
    def decorator(func: Callable) -> Callable:
        calls = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            # Remove old calls
            nonlocal calls
            calls = [t for t in calls if now - t < period]

            if len(calls) >= max_calls:
                return {
                    "error": "Rate limit exceeded",
                    "code": "RATE_LIMITED",
                    "retry_after": period - (now - calls[0])
                }

            calls.append(now)
            return func(*args, **kwargs)

        wrapper._rate_limited = True
        return wrapper
    return decorator


def transaction(func: Callable) -> Callable:
    """Decorator to wrap function in a transaction context."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        context = kwargs.get('_context', {})
        db = context.get('database')

        if db and hasattr(db, 'begin_transaction'):
            transaction_id = db.begin_transaction()
            try:
                result = func(*args, **kwargs)
                if isinstance(result, dict) and 'error' in result:
                    db.rollback_transaction(transaction_id)
                else:
                    db.commit_transaction(transaction_id)
                return result
            except Exception as e:
                db.rollback_transaction(transaction_id)
                raise
        else:
            return func(*args, **kwargs)

    wrapper._transactional = True
    return wrapper
