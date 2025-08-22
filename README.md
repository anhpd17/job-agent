# Job Assistant Agent

Ứng dụng hỗ trợ tìm việc làm sử dụng AI để tự động hóa các tác vụ như tìm việc, viết email, tạo CV, đánh giá CV và thống kê công ty.

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/anhpd17/job-agent.git
cd job-agent
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Thiết lập môi trường:
- Copy file `.env.example` thành `.env`:
```bash
cp .env.example .env
```
- Mở file `.env` và cập nhật các biến môi trường:
  - `OPENAI_API_KEY`: API key của OpenAI (bắt buộc)
  - Các biến khác có thể giữ nguyên giá trị mặc định

4. Chạy ứng dụng:
```bash
python app.py
```

Ứng dụng sẽ chạy tại địa chỉ: http://localhost:8501

## Tính năng

1. **Tìm việc**: Tìm kiếm việc làm phù hợp dựa trên mô tả công việc, mức lương, địa điểm và kinh nghiệm.
2. **Viết email**: Tự động tạo email xin việc chuyên nghiệp.
3. **Đánh giá CV**: Phân tích và đánh giá CV của bạn.
4. **Thống kê công ty**: Tìm kiếm và phân tích các công ty phù hợp.
5. **Tạo CV**: Tự động tạo CV từ thông tin cá nhân.

## Lưu ý bảo mật

- **KHÔNG** commit file `.env` vào repository
- Luôn sử dụng file `.env.example` làm mẫu và copy thành `.env` local
- Bảo vệ API key và thông tin nhạy cảm khác
