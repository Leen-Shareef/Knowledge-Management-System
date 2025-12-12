# tests/unit/test_logic.py

import pytest
from rag_pipeline.utils import get_rbac_metadata

# --- TEST 1: UNIT TEST FOR RBAC LOGIC ---
# Requirement: "Test that the metadata filter actually blocks IT docs from HR users"
# We test the logic function directly to ensure it labels files correctly.
def test_rbac_metadata_logic():
    # Case A: HR Document
    metadata_hr = get_rbac_metadata("data/HR_Policy_2025.pdf")
    assert metadata_hr["role"] == "HR_Employee"
    assert metadata_hr["department"] == "HR"

    # Case B: IT Document
    metadata_it = get_rbac_metadata("data/IT_Security_Protocols.pdf")
    assert metadata_it["role"] == "IT_Tech"
    assert metadata_it["department"] == "IT"

    # Case C: Sales Document
    metadata_sales = get_rbac_metadata("data/Client_Case_Studies.pdf")
    assert metadata_sales["role"] == "Sales_Team"