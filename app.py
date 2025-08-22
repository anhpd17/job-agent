from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from agent.job_agent import JobAssistantAgent, JobModule, EmailModule, CVModule, CompanyModule
from agent.utils import get_openai_api_key

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Cấu hình CORS
CORS(app, resources={
    r"/*": {  # Cho phép tất cả các route
        "origins": ["http://127.0.0.1:5500", "http://localhost:5500"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Check if OpenAI API key is available
try:
    api_key = get_openai_api_key()
except ValueError as e:
    print(f"Error: {str(e)}")
    api_key = None

# Initialize agent
agent = JobAssistantAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tim-viec')
def tim_viec():
    return render_template('tim_viec.html')

@app.route('/viet-email')
def viet_email():
    return render_template('viet_email.html')

@app.route('/danh-gia-cv')
def danh_gia_cv():
    return render_template('danh_gia_cv.html')

@app.route('/thong-ke-cong-ty')
def thong_ke_cong_ty():
    return render_template('thong_ke_cong_ty.html')

@app.route('/tao-cv')
def tao_cv():
    return render_template('tao_cv.html')

# API endpoints
@app.route('/api/tim-viec', methods=['POST'])
def api_tim_viec():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Không có dữ liệu được gửi lên"}), 400
            
        job_module = JobModule()
        
        result = job_module.find_jobs(
            job_description=data.get('jobDescription', ''),
            salary=data.get('salary', ''),
            location=data.get('location', ''),
            experience=data.get('experience', 0)
        )
        
        return jsonify({"result": result})
    except Exception as e:
        print(f"Error in /api/tim-viec: {str(e)}")
        return jsonify({"error": "Có lỗi xảy ra khi xử lý yêu cầu"}), 500

@app.route('/api/viet-email', methods=['POST'])
def api_viet_email():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Không có dữ liệu được gửi lên"}), 400
            
        email_module = EmailModule()
        
        result = email_module.write_application_email(
            job_title=data.get('job_title', ''),
            company=data.get('company', ''),
            skills=data.get('skills', '')
        )
        
        return jsonify({"email": result})
    except Exception as e:
        print(f"Error in /api/viet-email: {str(e)}")
        return jsonify({"error": "Có lỗi xảy ra khi xử lý yêu cầu"}), 500

@app.route('/api/danh-gia-cv', methods=['POST'])
def api_danh_gia_cv():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Không có dữ liệu được gửi lên"}), 400
            
        cv_module = CVModule()
        
        result = cv_module.evaluate_cv(
            cv_text=data.get('cv_text', ''),
            job_description=data.get('job_description', '')
        )
        
        return jsonify({"evaluation": result})
    except Exception as e:
        print(f"Error in /api/danh-gia-cv: {str(e)}")
        return jsonify({"error": "Có lỗi xảy ra khi xử lý yêu cầu"}), 500

@app.route('/api/thong-ke-cong-ty', methods=['POST'])
def api_thong_ke_cong_ty():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Không có dữ liệu được gửi lên"}), 400
            
        company_module = CompanyModule()
        
        result = company_module.find_top_companies(
            skills=data.get('skills', ''),
            industry=data.get('industry', ''),
            location=data.get('location', '')
        )
        
        return jsonify({"companies": result})
    except Exception as e:
        print(f"Error in /api/thong-ke-cong-ty: {str(e)}")
        return jsonify({"error": "Có lỗi xảy ra khi xử lý yêu cầu"}), 500

@app.route('/api/tao-cv', methods=['POST'])
def api_tao_cv():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Không có dữ liệu được gửi lên"}), 400
            
        cv_module = CVModule()
        
        result = cv_module.create_cv(
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            education=data.get('education', ''),
            experience=data.get('experience', ''),
            skills=data.get('skills', '')
        )
        
        return jsonify({"cv": result})
    except Exception as e:
        print(f"Error in /api/tao-cv: {str(e)}")
        return jsonify({"error": "Có lỗi xảy ra khi xử lý yêu cầu"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8501)