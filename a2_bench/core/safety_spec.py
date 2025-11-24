"""Safety specification system for A²-Bench."""

from typing import List, Callable, Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import re


class PropertyType(Enum):
    """Types of safety properties."""
    INVARIANT = "invariant"
    TEMPORAL = "temporal"
    SECURITY = "security"
    COMPLIANCE = "compliance"


class SafetyProperty(ABC):
    """Abstract base class for safety properties."""

    def __init__(self, name: str, severity: float, description: str = ""):
        """Initialize safety property.

        Args:
            name: Property name
            severity: Severity level (0.0 to 1.0)
            description: Human-readable description
        """
        self.name = name
        self.severity = min(1.0, max(0.0, severity))
        self.description = description

    @abstractmethod
    def evaluate(self, *args, **kwargs) -> bool:
        """Evaluate if the property holds.

        Returns:
            True if property is satisfied, False otherwise
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', severity={self.severity})"


class Invariant(SafetyProperty):
    """Safety invariant that must always hold."""

    def __init__(self,
                 name: str,
                 severity: float,
                 predicate: Callable[[Dict], bool],
                 description: str = ""):
        """Initialize invariant.

        Args:
            name: Invariant name
            severity: Violation severity (0.0 to 1.0)
            predicate: Function that takes state and returns bool
            description: Human-readable description
        """
        super().__init__(name, severity, description)
        self.predicate = predicate

    def evaluate(self, state: Dict) -> bool:
        """Evaluate invariant against current state.

        Args:
            state: Current environment state

        Returns:
            True if invariant holds, False otherwise
        """
        try:
            return self.predicate(state)
        except Exception:
            # If evaluation fails, consider invariant violated
            return False


class TemporalProperty(SafetyProperty):
    """Temporal safety property (e.g., action ordering)."""

    def __init__(self,
                 name: str,
                 severity: float,
                 formula: str,
                 description: str = ""):
        """Initialize temporal property.

        Args:
            name: Property name
            severity: Violation severity (0.0 to 1.0)
            formula: LTL-like formula string
            description: Human-readable description
        """
        super().__init__(name, severity, description)
        self.formula = formula
        self._parse_formula()

    def _parse_formula(self):
        """Parse the formula to extract components."""
        self._formula_type = None
        self._actions = []

        if self.formula.startswith("Always(Before("):
            self._formula_type = "always_before"
            match = re.search(r'Before\("([^"]+)",\s*"([^"]+)"\)', self.formula)
            if match:
                self._actions = [match.group(1), match.group(2)]

        elif self.formula.startswith("Never("):
            self._formula_type = "never"
            match = re.search(r'Never\((.+)\)', self.formula)
            if match:
                self._condition = match.group(1)

        elif self.formula.startswith("Eventually("):
            self._formula_type = "eventually"
            match = re.search(r'Eventually\("([^"]+)"\)', self.formula)
            if match:
                self._actions = [match.group(1)]

    def evaluate(self, action: str, history: List[Dict], state: Dict) -> bool:
        """Evaluate temporal property.

        Args:
            action: Current action being performed
            history: History of previous states/actions
            state: Current state

        Returns:
            True if property holds, False otherwise
        """
        if self._formula_type == "always_before":
            # Always(Before(A, B)) - A must occur before B
            action_a, action_b = self._actions

            if action == action_b or (isinstance(action, dict) and action.get('type') == action_b):
                # Check if action_a occurred before
                for entry in history:
                    entry_action = entry.get('action', {})
                    if isinstance(entry_action, dict):
                        if entry_action.get('type') == action_a:
                            return True
                    elif entry_action == action_a:
                        return True
                return False
            return True

        elif self._formula_type == "never":
            # Never(condition) - condition must never be true
            try:
                # Safely evaluate condition
                result = eval(self._condition, {
                    'state': state,
                    'action': action,
                    'And': lambda *args: all(args),
                    'Or': lambda *args: any(args),
                    'Not': lambda x: not x
                })
                return not result
            except Exception:
                return True  # If evaluation fails, assume property holds

        elif self._formula_type == "eventually":
            # Eventually(A) - A must eventually occur (checked at end)
            # This is typically checked at episode end, so we always return True during execution
            return True

        return True


class SecurityPolicy:
    """Security policy specification including RBAC and information flow."""

    def __init__(self):
        """Initialize security policy."""
        self.rbac: Dict[str, List[str]] = {}  # action -> required roles
        self.information_flow: List[Dict] = []  # flow restrictions
        self.audit_requirements: Dict[str, bool] = {}  # action -> requires audit
        self.encryption_requirements: List[str] = []  # operations requiring encryption

    def add_rbac_rule(self, action: str, roles: List[str]):
        """Add role-based access control rule.

        Args:
            action: Action name
            roles: List of roles allowed to perform action
        """
        self.rbac[action] = roles

    def add_flow_restriction(self, info_type: str, prohibited_destinations: List[str]):
        """Add information flow restriction.

        Args:
            info_type: Type of information (e.g., 'PHI', 'PII')
            prohibited_destinations: Destinations where info cannot flow
        """
        self.information_flow.append({
            'type': info_type,
            'prohibited': prohibited_destinations
        })

    def add_encryption_requirement(self, operation: str):
        """Add encryption requirement for operation.

        Args:
            operation: Operation that requires encryption
        """
        self.encryption_requirements.append(operation)

    def get_required_roles(self, action: str) -> List[str]:
        """Get roles required for action.

        Args:
            action: Action name

        Returns:
            List of required roles (empty if no restriction)
        """
        return self.rbac.get(action, [])

    def violates_information_flow(self, action: str, state: Dict) -> bool:
        """Check if action violates information flow policy.

        Args:
            action: Action being performed
            state: Current state

        Returns:
            True if violation detected, False otherwise
        """
        # Check if sensitive data is flowing to prohibited destinations
        if 'write_log' in action or 'export' in action:
            data = state.get('pending_data', '')
            for restriction in self.information_flow:
                if restriction['type'].lower() in str(data).lower():
                    for dest in restriction['prohibited']:
                        if dest in action:
                            return True
        return False

    def requires_encryption(self, operation: str) -> bool:
        """Check if operation requires encryption.

        Args:
            operation: Operation name

        Returns:
            True if encryption required
        """
        return operation in self.encryption_requirements


class ComplianceRule(SafetyProperty):
    """Regulatory compliance rule."""

    def __init__(self,
                 name: str,
                 regulation: str,
                 requirement: Callable[[str, Dict], bool],
                 description: str = ""):
        """Initialize compliance rule.

        Args:
            name: Rule name
            regulation: Regulation name (e.g., 'HIPAA', 'GDPR')
            requirement: Function(action, state) -> bool
            description: Human-readable description
        """
        super().__init__(name, severity=0.9, description=description)
        self.regulation = regulation
        self.requirement = requirement

    def evaluate(self, action: str, state: Dict) -> bool:
        """Evaluate compliance rule.

        Args:
            action: Action being performed
            state: Current state

        Returns:
            True if compliant, False otherwise
        """
        try:
            return self.requirement(action, state)
        except Exception:
            return False


@dataclass
class SafetySpec:
    """Complete safety specification for a domain."""

    name: str
    invariants: List[Invariant] = field(default_factory=list)
    temporal: List[TemporalProperty] = field(default_factory=list)
    security: SecurityPolicy = field(default_factory=SecurityPolicy)
    compliance: List[ComplianceRule] = field(default_factory=list)

    def add_invariant(self,
                      name: str,
                      severity: float,
                      predicate: Callable[[Dict], bool],
                      description: str = ""):
        """Add safety invariant.

        Args:
            name: Invariant name
            severity: Violation severity
            predicate: Evaluation function
            description: Human-readable description
        """
        self.invariants.append(Invariant(name, severity, predicate, description))

    def add_temporal(self,
                     name: str,
                     severity: float,
                     formula: str,
                     description: str = ""):
        """Add temporal property.

        Args:
            name: Property name
            severity: Violation severity
            formula: LTL-like formula
            description: Human-readable description
        """
        self.temporal.append(TemporalProperty(name, severity, formula, description))

    def add_compliance_rule(self,
                           name: str,
                           regulation: str,
                           requirement: Callable[[str, Dict], bool],
                           description: str = ""):
        """Add compliance rule.

        Args:
            name: Rule name
            regulation: Regulation name
            requirement: Evaluation function
            description: Human-readable description
        """
        self.compliance.append(ComplianceRule(name, regulation, requirement, description))

    def get_all_properties(self) -> List[SafetyProperty]:
        """Get all safety properties.

        Returns:
            List of all safety properties
        """
        return self.invariants + self.temporal + self.compliance

    def __repr__(self) -> str:
        return (f"SafetySpec(name='{self.name}', "
                f"invariants={len(self.invariants)}, "
                f"temporal={len(self.temporal)}, "
                f"compliance={len(self.compliance)})")
