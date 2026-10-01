from etl import parse_address, parse_salary, normalize_job_title
import numpy as np

# ==================================
# Test parse_salary
# ==================================

def test_parse_salary_VND():
    result = parse_salary("10 - 20 triệu")

    assert result.iloc[0] == 10_000_000
    assert result.iloc[1] == 20_000_000
    assert result.iloc[2] == "VND"

def test_parse_salary_usd():
    result = parse_salary("600 - 1,300 USD")

    assert result.iloc[0] == 600
    assert result.iloc[1] == 1300
    assert result.iloc[2] == "USD"

def test_parse_salary_negotiable():
    result = parse_salary("Thoả thuận")

    assert result.isna().all()


# ==================================
# Test normalize_job_title
# ==================================

def test_normalize_job_title():
    assert normalize_job_title(
        "Senior Java Developer"
    ) == "Software Developer"

    assert normalize_job_title(
        "Data Engineer"
    ) == "Data Engineer"

    assert normalize_job_title(
        "AI Engineer"
    ) == "AI/ML Engineer"
    

def test_unknown_job_title():
    assert normalize_job_title(
        "Marketing Executive"
    ) == "Other"


# ==================================
# Test parse_address
# ==================================

def test_parse_address():
    result = parse_address(
        "Hồ Chí Minh: Quận 9: Hà Nội: Cầu Giấy"
    )

    assert result == [
        {
            "city": "Hồ Chí Minh",
            "district": "Quận 9"
        },
        {
            "city": "Hà Nội",
            "district": "Cầu Giấy"
        }
    ]
    
def test_only_city_parse_address():
    result = parse_address(
        "Hồ Chí Minh"
    )

    assert result == [
        {
            "city": "Hồ Chí Minh",
            "district": np.nan
        },
    ]