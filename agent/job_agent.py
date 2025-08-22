from typing import Dict, List, Any, Annotated, TypedDict
import os
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from ddgs import DDGS
from agent.utils import get_openai_api_key, extract_json_from_text, format_job_results, format_company_results

# Định nghĩa các trạng thái
class AgentState(TypedDict):
    query: str
    context: Dict[str, Any]
    response: str
    next_step: str


class WebSearchInput(BaseModel):
    input:str = Field(description="Nội dung cần tìm kiếm trên internet để cập nhật thêm thông tin trả lời.")

@tool("web_search", args_schema=WebSearchInput, return_direct=True)
def web_search(input: str):
    """
    Tìm kiếm thông tin trên internet dựa vào nội dung người dùng cung cấp.
    """
    results = DDGS().text(input, max_results=5, region="vn-vi")
    return results


# Định nghĩa các module chức năng
class JobModule:
    def __init__(self):
        api_key = get_openai_api_key()
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-4.1", temperature=0.7)
    
    def find_jobs(self, job_description: str, salary: str = "", location: str = "", experience: int = 0) -> str:
        """Tìm kiếm công việc phù hợp dựa trên mô tả và yêu cầu"""
        prompt = PromptTemplate.from_template(
            """Bạn là một trợ lý tìm việc chuyên nghiệp. Hãy giúp tôi tìm kiếm công việc phù hợp dựa trên thông tin sau:
            Mô tả công việc: {job_description}
            Mức lương mong muốn: {salary}
            Địa điểm: {location}
            Kinh nghiệm: {experience} năm
            
            Hãy liệt kê 5 công việc phù hợp nhất, bao gồm:
            1. Tên vị trí
            2. Công ty
            3. Mức lương ước tính
            4. Yêu cầu chính
            5. Lý do phù hợp
            
            Trả lời bằng tiếng Việt và định dạng rõ ràng.
            Yêu cầu: trả về kết quả dưới dạng HTML (không được hiển thị các text kiểu thẻ trong html, nội dung phải chính xác chỉn chu từng câu chữ do kết quả trả về sẽ được tôi dùng để hiển thị trực tiếp lên cho người dùng đọc)
            , gạch thành các ý, format giao diện dễ đọc, có kết luận cuối cùng, hightline vào các ý chính, màu sắc của tiêu đề và nội dung bên trong không được trùng nhau
            
            Luôn trả về dạng HTML
            """
        )
        
        formatted_prompt = prompt.format(
            job_description=job_description,
            salary=salary,
            location=location,
            experience=experience
        )
        
        # react_agent = self.llm.bind_tools([web_search])
        
        # response = react_agent.invoke(formatted_prompt)
        
        
        response = self.llm.invoke(formatted_prompt)
        return response.content

class EmailModule:
    def __init__(self):
        api_key = get_openai_api_key()
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-4.1", temperature=0.7)
    
    def write_application_email(self, job_title: str, company: str, skills: str) -> str:
        """Viết email ứng tuyển dựa trên thông tin công việc và kỹ năng"""
        prompt = PromptTemplate.from_template(
            """Bạn là một chuyên gia viết email ứng tuyển. Hãy viết một email ứng tuyển chuyên nghiệp dựa trên thông tin sau:
            
            Vị trí ứng tuyển: {job_title}
            Công ty: {company}
            Kỹ năng và kinh nghiệm của ứng viên: {skills}
            
            Email cần có:
            1. Lời chào và giới thiệu bản thân
            2. Lý do quan tâm đến công ty và vị trí
            3. Tóm tắt kỹ năng và kinh nghiệm phù hợp
            4. Kết thúc lịch sự và mong muốn phỏng vấn
            
            Trả lời bằng tiếng Việt và định dạng rõ ràng."""
        )
        
        formatted_prompt = prompt.format(
            job_title=job_title,
            company=company,
            skills=skills
        )
        
        response = self.llm.invoke(formatted_prompt)
        return response.content

class CVModule:
    def __init__(self):
        api_key = get_openai_api_key()
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-4.1", temperature=0.7)
    
    def evaluate_cv(self, cv_text: str, job_description: str = "") -> str:
        """Đánh giá CV và đưa ra gợi ý cải thiện"""
        prompt = PromptTemplate.from_template(
            """Bạn là một chuyên gia tuyển dụng và đánh giá CV. Hãy đánh giá CV sau và đưa ra gợi ý cải thiện:
            
            CV: {cv_text}
            
            {job_context}
            
            Hãy đánh giá các khía cạnh sau:
            1. Định dạng và trì bày
            2. Nội dung và cách diễn đạt
            3. Kỹ năng và kinh nghiệm nổi bật
            4. Điểm cần cải thiện
            5. Gợi ý cụ thể để nâng cao chất lượng CV
            
            Trả lời bằng tiếng Việt và định dạng rõ ràng."""
        )
        
        job_context = ""
        if job_description:
            job_context = f"Mô tả công việc ứng tuyển: {job_description}"
        
        formatted_prompt = prompt.format(
            cv_text=cv_text,
            job_context=job_context
        )
        
        response = self.llm.invoke(formatted_prompt)
        return response.content
    
    def create_cv(self, name: str, email: str, phone: str, education: str, experience: str, skills: str) -> str:
        """Tạo CV dựa trên thông tin cung cấp"""
        prompt = PromptTemplate.from_template(
            """Bạn là một chuyên gia tạo CV. Hãy tạo một CV chuyên nghiệp dựa trên thông tin sau:
            
            Họ và tên: {name}
            Email: {email}
            Số điện thoại: {phone}
            Học vấn: {education}
            Kinh nghiệm làm việc: {experience}
            Kỹ năng: {skills}
            
            Hãy tạo một CV với định dạng rõ ràng, chuyên nghiệp, bao gồm:
            1. Thông tin cá nhân
            2. Mục tiêu nghề nghiệp
            3. Học vấn
            4. Kinh nghiệm làm việc
            5. Kỹ năng
            6. Thành tích (nếu có thể suy luận từ thông tin cung cấp)
            
            Trả lời bằng tiếng Việt và định dạng rõ ràng."""
        )
        
        formatted_prompt = prompt.format(
            name=name,
            email=email,
            phone=phone,
            education=education,
            experience=experience,
            skills=skills
        )
        
        response = self.llm.invoke(formatted_prompt)
        return response.content

class CompanyModule:
    def __init__(self):
        api_key = get_openai_api_key()
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-4.1", temperature=0.7)
    
    def find_top_companies(self, skills: str, industry: str, location: str = "") -> str:
        """Tìm và thống kê các công ty phù hợp với kỹ năng và ngành nghề"""
        prompt = PromptTemplate.from_template(
            """Bạn là một chuyên gia phân tích thị trường việc làm. Hãy liệt kê và phân tích các công ty hàng đầu phù hợp với thông tin sau:
            
            Kỹ năng và kinh nghiệm: {skills}
            Ngành nghề: {industry}
            Địa điểm: {location}
            
            Hãy liệt kê 10 công ty phù hợp nhất, bao gồm:
            1. Tên công ty
            2. Lĩnh vực hoạt động chính
            3. Quy mô công ty
            4. Lý do phù hợp với kỹ năng của ứng viên
            5. Cơ hội phát triển
            
            Trả lời bằng tiếng Việt và định dạng rõ ràng."""
        )
        
        formatted_prompt = prompt.format(
            skills=skills,
            industry=industry,
            location=location
        )
        
        response = self.llm.invoke(formatted_prompt)
        return response.content

# Định nghĩa các hàm xử lý cho đồ thị LangGraph
def route_to_module(state: AgentState) -> List[str]:
    """Định tuyến đến module xử lý phù hợp dựa trên next_step"""
    next_step = state["next_step"].strip().lower()
    if next_step == "find_jobs":
        return ["find_jobs"]
    elif next_step == "write_email":
        return ["write_email"]
    elif next_step == "evaluate_cv":
        return ["evaluate_cv"]
    elif next_step == "find_companies":
        return ["find_companies"]
    elif next_step == "create_cv":
        return ["create_cv"]
    else:
        return ["find_jobs"]  # Default fallback

def _build_graph(self):
    # Khởi tạo đồ thị
    workflow = StateGraph(AgentState)
    
    # Thêm các node
    workflow.add_node("process_query", process_query)
    workflow.add_node("find_jobs", execute_find_jobs)
    workflow.add_node("write_email", execute_write_email)
    workflow.add_node("evaluate_cv", execute_evaluate_cv)
    workflow.add_node("find_companies", execute_find_companies)
    workflow.add_node("create_cv", execute_create_cv)
    
    # Thêm các cạnh với conditional routing
    workflow.add_conditional_edges(
        "process_query",
        route_to_module,
        {
            "find_jobs": "find_jobs",
            "write_email": "write_email",
            "evaluate_cv": "evaluate_cv",
            "find_companies": "find_companies",
            "create_cv": "create_cv"
        }
    )
    
    # Thêm các cạnh kết thúc
    workflow.add_edge("find_jobs", END)
    workflow.add_edge("write_email", END)
    workflow.add_edge("evaluate_cv", END)
    workflow.add_edge("find_companies", END)
    workflow.add_edge("create_cv", END)
    
    # Thiết lập node bắt đầu
    workflow.set_entry_point("process_query")
    
    # Biên dịch đồ thị
    return workflow.compile()

def process_query(state: AgentState) -> AgentState:
    """Xử lý yêu cầu ban đầu và xác định bước tiếp theo"""
    query = state["query"]
    api_key = get_openai_api_key()
    llm = ChatOpenAI(api_key=api_key, model="gpt-4.1", temperature=0.2)
    
    prompt = PromptTemplate.from_template(
        """Dựa vào yêu cầu của người dùng, hãy xác định chức năng cần thực hiện:
        
        Yêu cầu: {query}
        
        Trả về một trong các giá trị sau:
        - find_jobs: Tìm kiếm việc làm
        - write_email: Viết email ứng tuyển
        - evaluate_cv: Đánh giá CV
        - find_companies: Tìm công ty phù hợp
        - create_cv: Tạo CV mới"""
    )
    
    formatted_prompt = prompt.format(query=query)
    response = llm.invoke(formatted_prompt)
    
    # Xác định bước tiếp theo
    state["next_step"] = response.content.strip()
    return state

def execute_find_jobs(state: AgentState) -> AgentState:
    """Thực hiện chức năng tìm việc"""
    job_module = JobModule()
    query = state["query"]
    
    # Phân tích yêu cầu để trích xuất thông tin
    api_key = get_openai_api_key()
    llm = ChatOpenAI(api_key=api_key, model="gpt-4.1", temperature=0.2)
    extract_prompt = PromptTemplate.from_template(
        """Từ yêu cầu của người dùng, hãy trích xuất các thông tin sau về công việc cần tìm:
        
        Yêu cầu: {query}
        
        Trả về kết quả theo định dạng JSON:
        {{
            "job_description": "Mô tả công việc",
            "salary": "Mức lương mong muốn (nếu có)",
            "location": "Địa điểm làm việc (nếu có)",
            "experience": "Số năm kinh nghiệm (nếu có, chỉ số)"
        }}"""
    )
    
    formatted_prompt = extract_prompt.format(query=query)
    extract_response = llm.invoke(formatted_prompt)
    
    # Phân tích kết quả JSON sử dụng hàm từ utils
    extracted_info = extract_json_from_text(extract_response.content)
    if not extracted_info:
        extracted_info = {
            "job_description": query,
            "salary": "",
            "location": "",
            "experience": 0
        }
    
    # Thực hiện tìm kiếm công việc
    response = job_module.find_jobs(
        job_description=extracted_info.get("job_description", query),
        salary=extracted_info.get("salary", ""),
        location=extracted_info.get("location", ""),
        experience=int(extracted_info.get("experience", 0))
    )
    
    state["response"] = response
    return state

def execute_write_email(state: AgentState) -> AgentState:
    """Thực hiện chức năng viết email ứng tuyển"""
    email_module = EmailModule()
    query = state["query"]
    
    # Phân tích yêu cầu để trích xuất thông tin
    llm = ChatOpenAI(model="gpt-4.1", temperature=0.2)
    extract_prompt = PromptTemplate.from_template(
        """Từ yêu cầu của người dùng, hãy trích xuất các thông tin sau về email ứng tuyển:
        
        Yêu cầu: {query}
        
        Trả về kết quả theo định dạng JSON:
        {{
            "job_title": "Vị trí công việc",
            "company": "Tên công ty",
            "skills": "Kỹ năng và kinh nghiệm của ứng viên"
        }}"""
    )
    
    formatted_prompt = extract_prompt.format(query=query)
    extract_response = llm.invoke(formatted_prompt)
    
    # Phân tích kết quả JSON (đơn giản hóa)
    import json
    try:
        extracted_info = json.loads(extract_response.content)
    except:
        extracted_info = {
            "job_title": "Vị trí ứng tuyển",
            "company": "Công ty",
            "skills": query
        }
    
    # Thực hiện viết email
    response = email_module.write_application_email(
        job_title=extracted_info.get("job_title", "Vị trí ứng tuyển"),
        company=extracted_info.get("company", "Công ty"),
        skills=extracted_info.get("skills", query)
    )
    
    state["response"] = response
    return state

def execute_evaluate_cv(state: AgentState) -> AgentState:
    """Thực hiện chức năng đánh giá CV"""
    cv_module = CVModule()
    query = state["query"]
    
    # Phân tích yêu cầu để trích xuất thông tin
    llm = ChatOpenAI(model="gpt-4.1", temperature=0.2)
    extract_prompt = PromptTemplate.from_template(
        """Từ yêu cầu của người dùng, hãy trích xuất các thông tin sau về CV cần đánh giá:
        
        Yêu cầu: {query}
        
        Trả về kết quả theo định dạng JSON:
        {{
            "cv_text": "Nội dung CV (nếu có)",
            "job_description": "Mô tả công việc ứng tuyển (nếu có)"
        }}"""
    )
    
    formatted_prompt = extract_prompt.format(query=query)
    extract_response = llm.invoke(formatted_prompt)
    
    # Phân tích kết quả JSON (đơn giản hóa)
    import json
    try:
        extracted_info = json.loads(extract_response.content)
    except:
        extracted_info = {
            "cv_text": query,
            "job_description": ""
        }
    
    # Thực hiện đánh giá CV
    response = cv_module.evaluate_cv(
        cv_text=extracted_info.get("cv_text", query),
        job_description=extracted_info.get("job_description", "")
    )
    
    state["response"] = response
    return state

def execute_find_companies(state: AgentState) -> AgentState:
    """Thực hiện chức năng tìm công ty phù hợp"""
    company_module = CompanyModule()
    query = state["query"]
    
    # Phân tích yêu cầu để trích xuất thông tin
    llm = ChatOpenAI(model="gpt-4.1", temperature=0.2)
    extract_prompt = PromptTemplate.from_template(
        """Từ yêu cầu của người dùng, hãy trích xuất các thông tin sau về công ty cần tìm:
        
        Yêu cầu: {query}
        
        Trả về kết quả theo định dạng JSON:
        {{
            "skills": "Kỹ năng và kinh nghiệm của ứng viên",
            "industry": "Ngành nghề quan tâm",
            "location": "Địa điểm làm việc (nếu có)"
        }}"""
    )
    
    formatted_prompt = extract_prompt.format(query=query)
    extract_response = llm.invoke(formatted_prompt)
    
    # Phân tích kết quả JSON (đơn giản hóa)
    import json
    try:
        extracted_info = json.loads(extract_response.content)
    except:
        extracted_info = {
            "skills": query,
            "industry": "Công nghệ thông tin",
            "location": ""
        }
    
    # Thực hiện tìm công ty
    response = company_module.find_top_companies(
        skills=extracted_info.get("skills", query),
        industry=extracted_info.get("industry", "Công nghệ thông tin"),
        location=extracted_info.get("location", "")
    )
    
    state["response"] = response
    return state

def execute_create_cv(state: AgentState) -> AgentState:
    """Thực hiện chức năng tạo CV"""
    cv_module = CVModule()
    query = state["query"]
    
    # Phân tích yêu cầu để trích xuất thông tin
    llm = ChatOpenAI(model="gpt-4.1", temperature=0.2)
    extract_prompt = PromptTemplate.from_template(
        """Từ yêu cầu của người dùng, hãy trích xuất các thông tin sau để tạo CV:
        
        Yêu cầu: {query}
        
        Trả về kết quả theo định dạng JSON:
        {{
            "name": "Họ và tên",
            "email": "Email",
            "phone": "Số điện thoại (nếu có)",
            "education": "Học vấn (nếu có)",
            "experience": "Kinh nghiệm làm việc",
            "skills": "Kỹ năng"
        }}"""
    )
    
    formatted_prompt = extract_prompt.format(query=query)
    extract_response = llm.invoke(formatted_prompt)
    
    # Phân tích kết quả JSON (đơn giản hóa)
    import json
    try:
        extracted_info = json.loads(extract_response.content)
    except:
        extracted_info = {
            "name": "Nguyễn Văn A",
            "email": "example@email.com",
            "phone": "",
            "education": "",
            "experience": query,
            "skills": ""
        }
    
    # Thực hiện tạo CV
    response = cv_module.create_cv(
        name=extracted_info.get("name", "Nguyễn Văn A"),
        email=extracted_info.get("email", "example@email.com"),
        phone=extracted_info.get("phone", ""),
        education=extracted_info.get("education", ""),
        experience=extracted_info.get("experience", query),
        skills=extracted_info.get("skills", "")
    )
    
    state["response"] = response
    return state

# Xây dựng đồ thị LangGraph
class JobAssistantAgent:
    def __init__(self):
        # Khởi tạo các module
        self.job_module = JobModule()
        self.email_module = EmailModule()
        self.cv_module = CVModule()
        self.company_module = CompanyModule()
        
        # Xây dựng đồ thị
        self.workflow = self._build_graph()
    
    def _build_graph(self):
        # Khởi tạo đồ thị
        workflow = StateGraph(AgentState)
        
        # Thêm các node
        workflow.add_node("process_query", process_query)
        workflow.add_node("find_jobs", execute_find_jobs)
        workflow.add_node("write_email", execute_write_email)
        workflow.add_node("evaluate_cv", execute_evaluate_cv)
        workflow.add_node("find_companies", execute_find_companies)
        workflow.add_node("create_cv", execute_create_cv)
        
        # Thêm các cạnh với conditional routing
        workflow.add_conditional_edges(
            "process_query",
            route_to_module,
            {
                "find_jobs": "find_jobs",
                "write_email": "write_email",
                "evaluate_cv": "evaluate_cv",
                "find_companies": "find_companies",
                "create_cv": "create_cv"
            }
        )
        
        # Thêm các cạnh kết thúc
        workflow.add_edge("find_jobs", END)
        workflow.add_edge("write_email", END)
        workflow.add_edge("evaluate_cv", END)
        workflow.add_edge("find_companies", END)
        workflow.add_edge("create_cv", END)
        
        # Thiết lập node bắt đầu
        workflow.set_entry_point("process_query")
        
        # Biên dịch đồ thị
        return workflow.compile()
    
    def find_jobs(self, job_description: str, salary: str = "", location: str = "", experience: int = 0) -> str:
        """Tìm kiếm công việc phù hợp"""
        return self.job_module.find_jobs(job_description, salary, location, experience)
    
    def write_application_email(self, job_title: str, company: str, skills: str) -> str:
        """Viết email ứng tuyển"""
        return self.email_module.write_application_email(job_title, company, skills)
    
    def evaluate_cv(self, cv_text: str, job_description: str = "") -> str:
        """Đánh giá CV"""
        return self.cv_module.evaluate_cv(cv_text, job_description)
    
    def find_top_companies(self, skills: str, industry: str, location: str = "") -> str:
        """Tìm công ty phù hợp"""
        return self.company_module.find_top_companies(skills, industry, location)
    
    def create_cv(self, name: str, email: str, phone: str, education: str, experience: str, skills: str) -> str:
        """Tạo CV"""
        return self.cv_module.create_cv(name, email, phone, education, experience, skills)
    
    def process(self, query: str) -> str:
        """Xử lý yêu cầu từ người dùng thông qua đồ thị LangGraph"""
        # Khởi tạo trạng thái
        state = {
            "query": query,
            "context": {},
            "response": "",
            "next_step": ""
        }
        
        # Thực thi đồ thị
        result = self.workflow.invoke(state)
        
        # Trả về kết quả
        return result["response"]