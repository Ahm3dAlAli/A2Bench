"""Healthcare tools for agents and users."""

from typing import Optional, List, Dict
from datetime import date

from a2_bench.domains.healthcare.database import HealthcareDatabase, Medication


class HealthcareAgentTools:
    """Tools available to healthcare agent."""

    def __init__(self, database: HealthcareDatabase):
        """Initialize agent tools.

        Args:
            database: Healthcare database
        """
        self.db = database

    def get_tools(self) -> Dict:
        """Get all agent tools as a dictionary.

        Returns:
            Dict mapping tool names to functions
        """
        return {
            'access_patient_record': self.access_patient_record,
            'prescribe_medication': self.prescribe_medication,
            'check_drug_interactions': self.check_drug_interactions,
            'check_allergies': self.check_allergies,
            'view_access_log': self.view_access_log,
            'verify_patient_identity': self.verify_patient_identity,
        }

    def access_patient_record(self,
                              patient_id: str,
                              reason: str = "",
                              current_user: str = "",
                              _context: Dict = None) -> Dict:
        """Access patient medical record with justification.

        Args:
            patient_id: Patient ID
            reason: Access justification
            current_user: User making request
            _context: Execution context

        Returns:
            Patient record or error
        """
        _context = _context or {}

        # Check authentication
        authenticated_users = _context.get('authenticated_users', set())
        if current_user not in authenticated_users:
            return {"error": "Authentication required", "code": "AUTH_REQUIRED"}

        # Check roles
        user_roles = _context.get('user_roles', {}).get(current_user, [])
        allowed_roles = ['doctor', 'nurse', 'nurse_practitioner', 'admin']
        if not any(role in user_roles for role in allowed_roles):
            return {
                "error": "Unauthorized: requires medical staff role",
                "code": "UNAUTHORIZED"
            }

        patient = self.db.get_patient(patient_id)
        if not patient:
            return {"error": "Patient not found", "code": "NOT_FOUND"}

        # Check authorization for sensitive access
        if not reason and current_user not in patient.authorized_users:
            return {
                "error": "Access denied: justification required for this patient",
                "code": "JUSTIFICATION_REQUIRED"
            }

        # Log access
        self.db.log_access(patient_id, current_user, "access_record", reason)

        return {
            "success": True,
            "patient_id": patient.patient_id,
            "name": patient.name,
            "dob": patient.dob.isoformat(),
            "allergies": [
                {
                    "allergen": a.allergen,
                    "severity": a.severity,
                    "reaction": a.reaction
                }
                for a in patient.allergies
            ],
            "active_medications": [
                {
                    "medication_id": m.medication_id,
                    "drug": m.drug_name,
                    "dosage": f"{m.dosage}{m.unit}",
                    "frequency": m.frequency
                }
                for m in patient.active_medications
            ],
            "conditions": [
                {
                    "name": c.name,
                    "status": c.status
                }
                for c in patient.medical_history
            ]
        }

    def prescribe_medication(self,
                             patient_id: str,
                             drug_name: str,
                             dosage: float,
                             unit: str = "mg",
                             frequency: str = "once daily",
                             current_user: str = "",
                             _context: Dict = None) -> Dict:
        """Prescribe medication with safety checks.

        Args:
            patient_id: Patient ID
            drug_name: Drug name
            dosage: Dosage amount
            unit: Dosage unit
            frequency: Frequency
            current_user: Prescribing user
            _context: Execution context

        Returns:
            Prescription result or error
        """
        _context = _context or {}

        # Check authentication
        authenticated_users = _context.get('authenticated_users', set())
        if current_user not in authenticated_users:
            return {"error": "Authentication required", "code": "AUTH_REQUIRED"}

        # Check roles (only doctors and NPs can prescribe)
        user_roles = _context.get('user_roles', {}).get(current_user, [])
        if not any(role in user_roles for role in ['doctor', 'nurse_practitioner']):
            return {
                "error": "Unauthorized: only doctors and nurse practitioners can prescribe",
                "code": "UNAUTHORIZED"
            }

        patient = self.db.get_patient(patient_id)
        if not patient:
            return {"error": "Patient not found", "code": "NOT_FOUND"}

        # Safety check: allergies
        allergy = self.db.check_drug_allergy(patient_id, drug_name)
        if allergy:
            return {
                "error": "Prescription blocked - allergy detected",
                "code": "ALLERGY_BLOCK",
                "allergen": allergy.allergen,
                "severity": allergy.severity,
                "reaction": allergy.reaction
            }

        # Safety check: drug interactions
        interactions = self.db.check_drug_interactions(patient_id, drug_name)
        if interactions:
            # Log warning but allow with confirmation
            pass

        # Create prescription
        med_id = f"M{len(patient.active_medications) + 1:03d}"
        medication = Medication(
            medication_id=med_id,
            drug_name=drug_name,
            generic_name=drug_name.lower(),
            dosage=dosage,
            unit=unit,
            frequency=frequency,
            prescriber_id=current_user,
            start_date=date.today(),
            end_date=None,
            interactions=[]
        )

        self.db.add_prescription(patient_id, medication)

        # Log prescription
        self.db.log_access(
            patient_id,
            current_user,
            "prescribe_medication",
            f"Prescribed {drug_name} {dosage}{unit}"
        )

        result = {
            "success": True,
            "prescription_id": med_id,
            "message": f"Prescribed {drug_name} {dosage}{unit} {frequency}",
            "patient_id": patient_id
        }

        if interactions:
            result["warnings"] = interactions

        return result

    def check_drug_interactions(self,
                                patient_id: str,
                                proposed_drug: str,
                                current_user: str = "",
                                _context: Dict = None) -> Dict:
        """Check for drug interactions.

        Args:
            patient_id: Patient ID
            proposed_drug: Drug to check
            current_user: User making request
            _context: Execution context

        Returns:
            Interaction check results
        """
        _context = _context or {}

        # Check authentication
        authenticated_users = _context.get('authenticated_users', set())
        if current_user not in authenticated_users:
            return {"error": "Authentication required", "code": "AUTH_REQUIRED"}

        patient = self.db.get_patient(patient_id)
        if not patient:
            return {"error": "Patient not found", "code": "NOT_FOUND"}

        interactions = self.db.check_drug_interactions(patient_id, proposed_drug)

        return {
            "success": True,
            "drug": proposed_drug,
            "patient_id": patient_id,
            "interactions_found": len(interactions) > 0,
            "interactions": interactions
        }

    def check_allergies(self,
                        patient_id: str,
                        drug_name: str,
                        current_user: str = "",
                        _context: Dict = None) -> Dict:
        """Check patient allergies for a drug.

        Args:
            patient_id: Patient ID
            drug_name: Drug to check
            current_user: User making request
            _context: Execution context

        Returns:
            Allergy check results
        """
        _context = _context or {}

        # Check authentication
        authenticated_users = _context.get('authenticated_users', set())
        if current_user not in authenticated_users:
            return {"error": "Authentication required", "code": "AUTH_REQUIRED"}

        patient = self.db.get_patient(patient_id)
        if not patient:
            return {"error": "Patient not found", "code": "NOT_FOUND"}

        allergy = self.db.check_drug_allergy(patient_id, drug_name)

        if allergy:
            return {
                "success": True,
                "allergy_found": True,
                "allergen": allergy.allergen,
                "severity": allergy.severity,
                "reaction": allergy.reaction,
                "drug_checked": drug_name
            }
        else:
            return {
                "success": True,
                "allergy_found": False,
                "drug_checked": drug_name,
                "message": "No allergy found for this drug"
            }

    def view_access_log(self,
                        patient_id: str,
                        current_user: str = "",
                        _context: Dict = None) -> Dict:
        """View patient record access log (admin only).

        Args:
            patient_id: Patient ID
            current_user: User making request
            _context: Execution context

        Returns:
            Access log or error
        """
        _context = _context or {}

        # Check authentication
        authenticated_users = _context.get('authenticated_users', set())
        if current_user not in authenticated_users:
            return {"error": "Authentication required", "code": "AUTH_REQUIRED"}

        # Check admin role
        user_roles = _context.get('user_roles', {}).get(current_user, [])
        if 'admin' not in user_roles:
            return {
                "error": "Unauthorized: admin role required",
                "code": "UNAUTHORIZED"
            }

        patient = self.db.get_patient(patient_id)
        if not patient:
            return {"error": "Patient not found", "code": "NOT_FOUND"}

        return {
            "success": True,
            "patient_id": patient_id,
            "access_log": [event.to_dict() for event in patient.access_log[-20:]]
        }

    def verify_patient_identity(self,
                                patient_id: str,
                                name: str = "",
                                dob: str = "",
                                current_user: str = "",
                                _context: Dict = None) -> Dict:
        """Verify patient identity.

        Args:
            patient_id: Patient ID
            name: Patient name for verification
            dob: Date of birth for verification
            current_user: User making request
            _context: Execution context

        Returns:
            Verification result
        """
        _context = _context or {}

        patient = self.db.get_patient(patient_id)
        if not patient:
            return {"error": "Patient not found", "code": "NOT_FOUND"}

        # Verify provided info matches
        name_match = not name or name.lower() in patient.name.lower()
        dob_match = not dob or dob == patient.dob.isoformat()

        if name_match and dob_match:
            return {
                "success": True,
                "verified": True,
                "patient_id": patient_id,
                "message": "Patient identity verified"
            }
        else:
            return {
                "success": True,
                "verified": False,
                "message": "Patient identity verification failed"
            }


class HealthcareUserTools:
    """Tools available to patient (user simulator)."""

    def __init__(self, database: HealthcareDatabase, patient_id: str):
        """Initialize user tools.

        Args:
            database: Healthcare database
            patient_id: Patient ID for this user
        """
        self.db = database
        self.patient_id = patient_id

    def get_tools(self) -> Dict:
        """Get all user tools as a dictionary.

        Returns:
            Dict mapping tool names to functions
        """
        return {
            'view_my_medications': self.view_my_medications,
            'view_my_allergies': self.view_my_allergies,
            'view_my_medical_history': self.view_my_medical_history,
            'request_prescription_refill': self.request_prescription_refill,
            'update_consent': self.update_consent,
        }

    def view_my_medications(self, _context: Dict = None, **kwargs) -> List[Dict]:
        """View own active medications.

        Returns:
            List of medications
        """
        patient = self.db.get_patient(self.patient_id)
        if not patient:
            return []

        return [
            {
                "medication_id": m.medication_id,
                "drug": m.drug_name,
                "dosage": f"{m.dosage}{m.unit}",
                "frequency": m.frequency,
                "start_date": m.start_date.isoformat()
            }
            for m in patient.active_medications
        ]

    def view_my_allergies(self, _context: Dict = None, **kwargs) -> List[Dict]:
        """View own allergies.

        Returns:
            List of allergies
        """
        patient = self.db.get_patient(self.patient_id)
        if not patient:
            return []

        return [
            {
                "allergen": a.allergen,
                "severity": a.severity,
                "reaction": a.reaction
            }
            for a in patient.allergies
        ]

    def view_my_medical_history(self, _context: Dict = None, **kwargs) -> List[Dict]:
        """View own medical history.

        Returns:
            List of conditions
        """
        patient = self.db.get_patient(self.patient_id)
        if not patient:
            return []

        return [
            {
                "condition": c.name,
                "status": c.status,
                "diagnosed": c.diagnosed_date.isoformat()
            }
            for c in patient.medical_history
        ]

    def request_prescription_refill(self,
                                    medication_id: str,
                                    _context: Dict = None,
                                    **kwargs) -> Dict:
        """Request medication refill.

        Args:
            medication_id: Medication ID

        Returns:
            Refill request result
        """
        patient = self.db.get_patient(self.patient_id)
        if not patient:
            return {"error": "Patient not found"}

        # Find medication
        med = next(
            (m for m in patient.active_medications if m.medication_id == medication_id),
            None
        )
        if not med:
            return {"error": "Medication not found"}

        return {
            "success": True,
            "message": f"Refill request submitted for {med.drug_name}",
            "medication_id": medication_id,
            "requires_approval": True,
            "estimated_ready": "24-48 hours"
        }

    def update_consent(self,
                       consent_to_share: bool,
                       _context: Dict = None,
                       **kwargs) -> Dict:
        """Update consent to share records.

        Args:
            consent_to_share: New consent status

        Returns:
            Update result
        """
        patient = self.db.get_patient(self.patient_id)
        if not patient:
            return {"error": "Patient not found"}

        patient.consent_to_share = consent_to_share

        return {
            "success": True,
            "message": f"Consent updated to {consent_to_share}",
            "consent_to_share": consent_to_share
        }
