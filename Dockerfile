FROM python3.7.7-slim
WORKDIR /Users/evanazevedo/workspace/amberdata
COPY * ./
RUN pip install -r requirements.txt
COPY . . 
EXPOSE 3000
CMD ["python", "src/main.py"]