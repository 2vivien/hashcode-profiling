from orientation.contracts.profile import StudentProfile

def test_profile_contract_rejects_out_of_range_dimension() -> None:
    try:
        StudentProfile(student_id="x", interests={"investigative": 1.5})
    except ValueError:
        return
    raise AssertionError("invalid profile was accepted")
