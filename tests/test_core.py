"""Tests for core A²-Bench components."""

import pytest
from a2_bench.core.safety_spec import SafetySpec, Invariant, TemporalProperty
from a2_bench.core.safety_monitor import SafetyMonitor, Violation
from a2_bench.core.environment import A2Environment


class TestSafetySpec:
    """Tests for SafetySpec."""

    def test_create_empty_spec(self):
        """Test creating empty safety spec."""
        spec = SafetySpec("test_spec")
        assert spec.name == "test_spec"
        assert len(spec.invariants) == 0
        assert len(spec.temporal) == 0

    def test_add_invariant(self):
        """Test adding invariant to spec."""
        spec = SafetySpec("test")
        spec.add_invariant(
            name="test_invariant",
            severity=0.8,
            predicate=lambda state: state.get('valid', True),
            description="Test invariant"
        )
        assert len(spec.invariants) == 1
        assert spec.invariants[0].name == "test_invariant"
        assert spec.invariants[0].severity == 0.8

    def test_invariant_evaluation(self):
        """Test invariant evaluation."""
        invariant = Invariant(
            name="test",
            severity=1.0,
            predicate=lambda state: state.get('safe', False)
        )

        # Should fail (safe=False by default)
        assert invariant.evaluate({}) == False

        # Should pass
        assert invariant.evaluate({'safe': True}) == True

    def test_add_temporal_property(self):
        """Test adding temporal property."""
        spec = SafetySpec("test")
        spec.add_temporal(
            name="auth_before_access",
            severity=0.9,
            formula='Always(Before("authenticate", "access"))'
        )
        assert len(spec.temporal) == 1

    def test_security_policy_rbac(self):
        """Test RBAC rules."""
        spec = SafetySpec("test")
        spec.security.add_rbac_rule("prescribe", ["doctor", "np"])

        roles = spec.security.get_required_roles("prescribe")
        assert "doctor" in roles
        assert "np" in roles

        # Non-existent action returns empty
        assert spec.security.get_required_roles("unknown") == []


class TestSafetyMonitor:
    """Tests for SafetyMonitor."""

    def test_monitor_creation(self):
        """Test creating safety monitor."""
        spec = SafetySpec("test")
        monitor = SafetyMonitor(spec)
        assert monitor.spec == spec
        assert len(monitor.violations) == 0

    def test_check_invariants(self):
        """Test invariant checking."""
        spec = SafetySpec("test")
        spec.add_invariant(
            name="must_be_safe",
            severity=1.0,
            predicate=lambda state: state.get('safe', False)
        )

        monitor = SafetyMonitor(spec)

        # Should detect violation
        violations = monitor.check_invariants({'safe': False})
        assert len(violations) == 1
        assert violations[0].type == 'safety_critical'
        assert violations[0].severity == 1.0

        # Should pass
        violations = monitor.check_invariants({'safe': True})
        assert len(violations) == 0

    def test_violation_summary(self):
        """Test violation summary generation."""
        spec = SafetySpec("test")
        spec.add_invariant("test", 1.0, lambda s: False)

        monitor = SafetyMonitor(spec)
        monitor.check_invariants({})

        summary = monitor.get_violation_summary()
        assert summary['total'] == 1
        assert summary['by_type']['safety_critical'] == 1

    def test_reset(self):
        """Test monitor reset."""
        spec = SafetySpec("test")
        spec.add_invariant("test", 1.0, lambda s: False)

        monitor = SafetyMonitor(spec)
        monitor.check_invariants({})
        assert len(monitor.violations) == 1

        monitor.reset()
        assert len(monitor.violations) == 0


class TestA2Environment:
    """Tests for A2Environment."""

    def test_environment_creation(self):
        """Test creating environment."""
        from a2_bench.domains.healthcare import HealthcareDomain

        domain = HealthcareDomain()
        env = domain.create_environment()

        assert env.domain == "healthcare"
        assert env.step_count == 0

    def test_environment_reset(self):
        """Test environment reset."""
        from a2_bench.domains.healthcare import HealthcareDomain

        domain = HealthcareDomain()
        env = domain.create_environment()

        # Take some steps
        env.step_count = 5

        # Reset
        env.reset()
        assert env.step_count == 0

    def test_set_user_role(self):
        """Test setting user roles."""
        from a2_bench.domains.healthcare import HealthcareDomain

        domain = HealthcareDomain()
        env = domain.create_environment()

        env.set_user_role("test_user", ["doctor", "admin"])

        roles = env.state['security']['user_roles'].get('test_user', [])
        assert "doctor" in roles
        assert "admin" in roles


class TestHealthcareDomain:
    """Tests for Healthcare domain."""

    def test_domain_creation(self):
        """Test creating healthcare domain."""
        from a2_bench.domains.healthcare import HealthcareDomain

        domain = HealthcareDomain()
        assert domain.name == "healthcare"

    def test_get_tasks(self):
        """Test getting tasks."""
        from a2_bench.domains.healthcare import HealthcareDomain

        domain = HealthcareDomain()
        tasks = domain.get_tasks()

        assert len(tasks) > 0
        assert all('id' in task for task in tasks)

    def test_allergy_check(self):
        """Test allergy checking in database."""
        from a2_bench.domains.healthcare import HealthcareDatabase

        db = HealthcareDatabase()

        # Patient P001 has penicillin allergy
        allergy = db.check_drug_allergy("P001", "penicillin")
        assert allergy is not None
        assert allergy.allergen == "penicillin"

        # Amoxicillin should also trigger (cross-reaction)
        allergy = db.check_drug_allergy("P001", "amoxicillin")
        assert allergy is not None

        # Patient P003 has no allergies
        allergy = db.check_drug_allergy("P003", "penicillin")
        assert allergy is None

    def test_patient_retrieval(self):
        """Test patient retrieval."""
        from a2_bench.domains.healthcare import HealthcareDatabase

        db = HealthcareDatabase()

        patient = db.get_patient("P001")
        assert patient is not None
        assert patient.name == "John Smith"

        # Non-existent patient
        patient = db.get_patient("P999")
        assert patient is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
