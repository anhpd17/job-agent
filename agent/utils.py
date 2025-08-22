import os
from typing import Dict, Any
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_openai_api_key() -> str:
    """Lấy OpenAI API key từ biến môi trường"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY không được cấu hình trong file .env")
    return api_key

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Trích xuất JSON từ văn bản"""
    try:
        # Tìm dấu ngoặc nhọn đầu tiên và cuối cùng
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            return {}
        
        json_str = text[start_idx:end_idx]
        return json.loads(json_str)
    except Exception as e:
        print(f"Lỗi khi trích xuất JSON: {e}")
        return {}

def format_job_results(jobs_data: Dict[str, Any]) -> str:
    """Định dạng kết quả tìm kiếm công việc"""
    if not jobs_data or not isinstance(jobs_data, dict):
        return "Không tìm thấy công việc phù hợp."
    
    result = "## Công việc phù hợp\n\n"
    
    for i, job in enumerate(jobs_data.get("jobs", []), 1):
        result += f"### {i}. {job.get('title', 'Không có tiêu đề')}\n"
        result += f"**Công ty:** {job.get('company', 'Không có thông tin')}\n"
        result += f"**Mức lương:** {job.get('salary', 'Không có thông tin')}\n"
        result += f"**Yêu cầu chính:** {job.get('requirements', 'Không có thông tin')}\n"
        result += f"**Lý do phù hợp:** {job.get('reason', 'Không có thông tin')}\n\n"
    
    return result

def format_company_results(companies_data: Dict[str, Any]) -> str:
    """Định dạng kết quả thống kê công ty"""
    if not companies_data or not isinstance(companies_data, dict):
        return "Không tìm thấy công ty phù hợp."
    
    result = "## Công ty phù hợp\n\n"
    
    for i, company in enumerate(companies_data.get("companies", []), 1):
        result += f"### {i}. {company.get('name', 'Không có tên')}\n"
        result += f"**Lĩnh vực:** {company.get('industry', 'Không có thông tin')}\n"
        result += f"**Quy mô:** {company.get('size', 'Không có thông tin')}\n"
        result += f"**Lý do phù hợp:** {company.get('reason', 'Không có thông tin')}\n"
        result += f"**Cơ hội phát triển:** {company.get('opportunities', 'Không có thông tin')}\n\n"
    
    return result