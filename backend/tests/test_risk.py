from app.schemas.job import JobInformation
from app.tools.risk_tools import calculate_risk


def test_payment_request_creates_high_weight_signal():
    job = JobInformation(payment_requested=True)
    score, signals = calculate_risk(job, "registration fee ₹2999")
    assert score >= 30
    assert any(s.signal_type == "PAYMENT_REQUEST" for s in signals)


def test_clean_text_has_no_payment_signal():
    job = JobInformation()
    score, signals = calculate_risk(job, "Python internship with no application fee.")
    assert not any(s.signal_type == "PAYMENT_REQUEST" for s in signals)
