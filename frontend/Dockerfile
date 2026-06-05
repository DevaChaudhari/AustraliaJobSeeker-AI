FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install streamlit requests python-docx pypdf
COPY . .
EXPOSE 8080
CMD ["streamlit", "run", "app.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]