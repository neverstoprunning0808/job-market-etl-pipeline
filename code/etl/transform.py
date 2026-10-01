import pandas as pd
import numpy as np
import re


def parse_salary(s):
    s = str(s).strip().lower()

    # na
    if pd.isna(s):
        return pd.Series([np.nan, np.nan, np.nan])

    # "Thỏa thuận"
    if "thoả thuận" in s or "thỎa thuận" in s:
        return pd.Series([np.nan, np.nan, np.nan])

    # Separate the numbers:
    numbers = re.findall(r"[\d.,]+", s)

    if not numbers:
        return pd.Series([np.nan, np.nan, np.nan])

    numbers = [float(x.replace(",", "")) for x in numbers]

    # currency:
    if "usd" in s:
        unit = "USD"
    elif "triệu" in s:
        unit = "VND"
        numbers = [x * 1_000_000 for x in numbers]

    if max(numbers) < 1_000_000:
        unit = "USD"
    else:
        unit = "VND"

    # X - Y:
    if len(numbers) >= 2:
        min_salary = numbers[0]
        max_salary = numbers[1]
    # Tới / Đến X:
    elif "tới" in s or "đến" in s:
        min_salary = np.nan
        max_salary = numbers[0]
    # Trên X:
    elif "trên" in s or "từ" in s:
        min_salary = numbers[0]
        max_salary = np.nan
    else:
        min_salary = numbers[0]
        max_salary = numbers[0]

    return pd.Series([min_salary, max_salary, unit])


def parse_address(address):
    cities = [
        "An Giang",
        "Bà Rịa - Vũng Tàu",
        "Bắc Giang",
        "Bắc Kạn",
        "Bạc Liêu",
        "Bắc Ninh",
        "Bến Tre",
        "Bình Định",
        "Bình Dương",
        "Bình Phước",
        "Bình Thuận",
        "Cà Mau",
        "Cần Thơ",
        "Cao Bằng",
        "Đà Nẵng",
        "Đắk Lắk",
        "Đắk Nông",
        "Điện Biên",
        "Đồng Nai",
        "Đồng Tháp",
        "Gia Lai",
        "Hà Giang",
        "Hà Nam",
        "Hà Nội",
        "Hà Tĩnh",
        "Hải Dương",
        "Hải Phòng",
        "Hậu Giang",
        "Hồ Chí Minh",
        "Hoà Bình",
        "Hưng Yên",
        "Khánh Hoà",
        "Kiên Giang",
        "Kon Tum",
        "Lai Châu",
        "Lâm Đồng",
        "Lạng Sơn",
        "Lào Cai",
        "Long An",
        "Nam Định",
        "Nghệ An",
        "Ninh Bình",
        "Ninh Thuận",
        "Phú Thọ",
        "Phú Yên",
        "Quảng Bình",
        "Quảng Nam",
        "Quảng Ngãi",
        "Quảng Ninh",
        "Quảng Trị",
        "Sóc Trăng",
        "Sơn La",
        "Tây Ninh",
        "Thái Bình",
        "Thái Nguyên",
        "Thanh Hoá",
        "Thừa Thiên Huế",
        "Tiền Giang",
        "Trà Vinh",
        "Tuyên Quang",
        "Vĩnh Long",
        "Vĩnh Phúc",
        "Yên Bái",
        "Nước Ngoài",
        "Toàn Quốc",
    ]  # 64 provinces + nationwide

    cities = set(cities)

    if pd.isna(address):
        return []

    parts = [x.strip() for x in re.split(r"[:,]", address)]

    result = []
    current_city = None
    city_has_district = False

    #   if len(parts) == 1:
    #     result.append({"city": parts[0], "district": np.nan})

    for part in parts:
        if part in cities:
            if current_city is not None and not city_has_district:
                result.append({"city": current_city, "district": np.nan})
            current_city = part
            city_has_district = False

        elif current_city is not None:
            result.append({"city": current_city, "district": part})
            city_has_district = True

    if current_city is not None and not city_has_district:
        result.append({"city": current_city, "district": np.nan})

    return result


def normalize_job_title(title):
    if pd.isna(title):
        return "Other"

    title = str(title).lower().strip()

    # AI / ML
    if any(
        x in title
        for x in [
            "ai engineer",
            "ai enigneer",
            "machine learning",
            "ml engineer",
            "artificial intelligence",
            "trí tuệ nhân tạo",
            "computer vision",
            "ai intern",
            "thực tập sinh ai",
        ]
    ):
        return "AI/ML Engineer"

    # Data Science
    elif any(x in title for x in ["data scientist", "khoa học dữ liệu"]):
        return "Data Scientist"

    # Data Engineer / Big Data
    elif any(
        x in title
        for x in ["data engineer", "big data", "kỹ sư dữ liệu", "data center engineer"]
    ):
        return "Data Engineer"

    # Database
    elif any(
        x in title
        for x in [
            "database administrator",
            "database engineer",
            "dba",
            "quản trị cơ sở dữ liệu",
            "quản trị dữ liệu oracle",
        ]
    ):
        return "Database Administrator"

    # BI
    elif any(
        x in title
        for x in [
            "business intelligence",
            "bi analyst",
            "chuyên viên cao cấp bi",
            "powerbi",
        ]
    ):
        return "BI Analyst"

    # Data
    elif any(
        x in title
        for x in [
            "data analyst",
            "phân tích dữ liệu",
            "data governance",
            "data manager",
            "data admin",
            "thực tập sinh data",
            "xử lý dữ liệu",
        ]
    ):
        return "Data Analyst"

    # Cybersecurity
    elif any(
        x in title
        for x in [
            "security",
            "cybersecurity",
            "pentest",
            "soc",
            "an toàn thông tin",
            "an ninh mạng",
            "bảo mật",
        ]
    ):
        return "Cybersecurity"

    # Cloud
    elif any(
        x in title
        for x in [
            "cloud engineer",
            "cloud specialist",
            "cloud support",
            "triển khai cloud",
            "vận hành cloud",
            "aws engineer",
            "azure engineer",
            "cloud vmware",
            "cao cấp cloud",
        ]
    ):
        return "Cloud Engineer"

    # DevOps / SRE
    elif any(x in title for x in ["devops", "sre", "site reliability"]):
        return "DevOps/SRE"

    # Network
    elif any(
        x in title
        for x in [
            "network engineer",
            "network administrator",
            "system network",
            "thực tập sinh network",
            "quản trị mạng",
            "kỹ thuật mạng",
            "kỹ sư mạng",
            "hệ thống mạng",
            "networking",
            "dịch vụ network",
            "truyền dẫn quang",
            "optical network",
        ]
    ):
        return "Network Engineer"

    # System / Infrastructure
    elif any(
        x in title
        for x in [
            "system engineer",
            "system admin",
            "system administrator",
            "server engineer",
            "infra engineer",
            "infra lead",
            "infrastructure",
            "it system",
            "kỹ sư hệ thống",
            "quản trị hệ thống",
            "it infra",
            "linux engineer",
            "linux kernel",
            "system integration",
            "mảng system",
            "information systems",
            "quản lý hệ thống thông tin",
            "it administrator",
        ]
    ):
        return "System/Infrastructure"

    # Business Analyst
    elif any(
        x in title
        for x in [
            "business analyst",
            "business analysis",
            "business analyses",
            "it business analyst",
            "fresher ba",
            "system analyst",
            "phân tích nghiệp vụ",
        ]
    ):
        return "Business Analyst"

    # QA / QC
    elif any(
        x in title
        for x in [
            "qa",
            "qc",
            "tester",
            "testing",
            "test engineer",
            "test lead",
            "software test",
            "automation test",
            "quality assurance",
            "software quality",
            "kiểm thử",
            "verification engineer",
        ]
    ):
        return "QA/Tester"

    # UI / UX
    elif any(
        x in title
        for x in [
            "ui/ux",
            "ux/ui",
            "ui ux",
            "ui/ ux",
            "ui designer",
            "ux designer",
            "product designer",
            "thiết kế website",
            "web designer",
        ]
    ):
        return "UI/UX Designer"

    # BRSE
    elif any(x in title for x in ["brse", "bridge system engineer", "kỹ sư cầu nối"]):
        return "Bridge System Engineer"

    # Architect
    elif any(x in title for x in ["solution architect", "software architect"]):
        return "Solution Architect"

    # Project Management
    elif any(
        x in title
        for x in [
            "project manager",
            "project leader",
            "project coordinator",
            "điều phối dự án",
            "quản lý dự án",
            "quản trị dự án",
            "quản lý triển khai dự án",
            "iteration manager",
            "delivery manager",
            "triển khai dự án",
        ]
    ):
        return "Project Management"

    # Scrum
    elif "scrum master" in title:
        return "Scrum Master"

    # Product
    elif any(
        x in title
        for x in ["product owner", "game product manager", "phân tích sản phẩm"]
    ):
        return "Product"

    # Tech Lead
    elif any(
        x in title
        for x in [
            "tech lead",
            "technical lead",
            "technical leader",
            "lead engineer",
            "mobile tech lead",
        ]
    ):
        return "Tech Lead"

    # IT Management
    elif any(
        x in title
        for x in [
            "it manager",
            "system manager",
            "trưởng phòng it",
            "trưởng bộ phận it",
            "chief technology officer",
            "technical manager",
        ]
    ):
        return "IT Management"

    # IT Communicator
    elif any(
        x in title
        for x in ["it comtor", "comtor it", "comtor tiếng nhật", "it communicator"]
    ):
        return "IT Communicator"

    # Software Implementation / Operation
    elif any(
        x in title
        for x in [
            "triển khai phần mềm",
            "triển khai erp",
            "triển khai hệ thống phần mềm",
            "triển khai và hỗ trợ phần mềm",
            "triển khai chuyển giao phần mềm",
            "vận hành hệ thống phần mềm",
            "quản trị vận hành phần mềm",
            "quản trị ứng dụng",
            "it operator",
            "vận hành web-app",
        ]
    ):
        return "Software Implementation"

    # Full-stack
    elif any(x in title for x in ["full-stack", "full stack", "fullstack"]):
        return "Full-stack Developer"

    # Frontend
    elif any(
        x in title
        for x in [
            "frontend",
            "front-end",
            "front end",
            "front - end",
            "font-end",
            "react js",
            "reactjs",
            "react.js",
            "angular",
            "vuejs",
            "vue.js",
            "vue3",
        ]
    ):
        return "Frontend Developer"

    # Backend
    elif any(x in title for x in ["backend", "back-end", "back end", "nestjs"]):
        return "Backend Developer"

    # Mobile
    elif any(
        x in title
        for x in [
            "android",
            "ios",
            "swift",
            "react native",
            "flutter",
            "lập trình mobile",
            "mobile intern",
            "thực tập sinh mobile",
        ]
    ):
        return "Mobile Developer"

    # Embedded / IoT
    elif any(
        x in title
        for x in ["embedded", "phần mềm nhúng", "fpga", "bsp", "iot engineer"]
    ):
        return "Embedded/IoT Developer"

    # Game
    elif any(
        x in title
        for x in [
            "game developer",
            "game engineer",
            "game designer",
            "game design",
            "unity",
            "cocos creator",
        ]
    ):
        return "Game Development"

    # Software Developer - generic, phải gần cuối
    elif any(
        x in title
        for x in [
            "software engineer",
            "software developer",
            "software mid-level engineer",
            "developer",
            "dev ",
            "lập trình",
            "kỹ sư phần mềm",
            "kỹ thuật phần mềm" "chuyên viên phần mềm",
            "phát triển phần mềm",
            "phát triển ứng dụng",
            "website developer",
            "website deverloper",
            ".net",
            "dotnet",
            "java",
            "php",
            "laravel",
            "nodejs",
            "node.js",
            "python",
            "golang",
            "ruby on rails",
            "c++",
            "c#",
            "wpf",
            "smartcontract",
        ]
    ):
        return "Software Developer"

    # IT Support
    elif any(
        x in title
        for x in [
            "technical support",
            "support engineer",
            "it support",
            "it customer support",
            "application support",
            "system monitor support",
            "service desk",
            "helpdesk",
            "help desk",
            "hỗ trợ kỹ thuật",
            "hỗ trợ kĩ thuật",
            "hỗ trợ người dùng",
            "hỗ trợ công nghệ thông tin",
            "it nội bộ",
        ]
    ):
        return "IT Support"

    # Hardware / IT Technician
    elif any(
        x in title
        for x in [
            "kỹ thuật máy tính",
            "kỹ thuật viên it",
            "kỹ thuật phần cứng",
            "phần cứng - mạng",
            "cntt phần cứng",
            "sửa chữa máy tính",
            "nhân viên vi tính",
        ]
    ):
        return "IT Hardware/Technician"

    # Generic IT - phải gần cuối
    elif any(
        x in title
        for x in [
            "nhân viên it",
            "chuyên viên it",
            "kỹ sư it",
            "it specialist",
            "chuyên viên cntt",
            "nhân viên cntt",
            "kỹ sư cntt",
            "công nghệ thông tin",
            "thực tập sinh it",
        ]
    ):
        return "IT General"

    # IT Infrastructure / Operations
    elif any(
        x in title
        for x in [
            "kỹ sư infra",
            "hạ tầng cntt",
            "triển khai hạ tầng",
            "operations engineer",
            "operation fresher",
            "vận hành dịch vụ",
            "it service coordinator",
        ]
    ):
        return "System/Infrastructure"

    # IT / Software generic
    elif any(
        x in title
        for x in [
            "cộng tác viên it",
            "thực tập sinh công nghệ",
            "trưởng nhóm it web",
            "kỹ thuật phần mềm",
            "phát triển website",
        ]
    ):
        return "IT General"

    # Low-code / Enterprise Application
    elif any(x in title for x in ["powerapps", "microsoft ax", "d365"]):
        return "Software Developer"

    # Blockchain
    elif any(x in title for x in ["blockchain", "smart contract", "smartcontract"]):
        return "Software Developer"

    # IT Hardware / Technical
    elif any(
        x in title
        for x in [
            "kỹ thuật internet",
            "kỹ thuật máy in",
            "kỹ thuật máy photocopy",
            "sửa chữa máy in",
            "sửa chữa máy tính",
            "kỹ thuật viên tại trung tâm bảo hành",
        ]
    ):
        return "IT Hardware/Technician"

    # Telecom / Network
    elif any(x in title for x in ["kỹ sư truyền dẫn", "kỹ thuật viễn thông", "voip"]):
        return "Network Engineer"

    # R&D / Robotics
    elif any(
        x in title
        for x in [
            "kỹ sư robotics",
            "research & development",
            "nhân viên r&d",
            "nghiên cứu và phát triển công nghệ",
        ]
    ):
        return "R&D Engineer"

    # Game technical/design
    elif any(
        x in title
        for x in [
            "2d game",
            "3d game",
            "game artist",
            "game animation",
            "vận hành game",
            "thiết kế kịch bản game",
        ]
    ):
        return "Game Development"

    # Software
    elif any(x in title for x in ["chuyên viên phần mềm"]):
        return "Software Developer"

    # IT Automation
    elif any(x in title for x in ["tự động hóa it", "tự động hoá it"]):
        return "System/Infrastructure"

    # Hardware Engineer
    elif any(x in title for x in ["thiết kế phần cứng"]):
        return "IT Hardware/Technician"

    # IT Project
    elif any(x in title for x in ["project assistant - it software"]):
        return "Project Management"

    # Technical / Engineering tools
    elif any(
        x in title
        for x in ["cad engineer", "cae engineer", "phát triển tool trong cad"]
    ):
        return "Engineering/CAD"

    # IT-related training
    elif any(
        x in title
        for x in ["giảng viên ccna", "giáng viên khoa cntt", "giảng viên khoa cntt"]
    ):
        return "IT Education"

    return "Other"


def transform_data(df):
    try:
        new_df = df.copy()

        new_df = new_df.drop_duplicates()

        new_df[["min_salary", "max_salary", "salary_unit"]] = new_df["salary"].apply(
            parse_salary
        )
        new_df["job_group"] = new_df["job_title"].apply(normalize_job_title)
        new_df["location"] = new_df["address"].apply(parse_address)

        location_df = new_df.explode("location")

        location_df["city"] = location_df["location"].apply(
            lambda x: x["city"] if isinstance(x, dict) else None
        )
        location_df["district"] = location_df["location"].apply(
            lambda x: x["district"] if isinstance(x, dict) else None
        )

        location_df = location_df.drop(columns=["location"])

        print(f"Transformed {len(location_df)} rows successfully!")

        return location_df

    except KeyError as e:
        raise ValueError(f"Missing required columns: {e}")

    except Exception as e:
        raise RuntimeError(f"Transform failed: {e}")
