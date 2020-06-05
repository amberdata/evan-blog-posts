FROM python:3.7.7-slim
WORKDIR /Users/evanazevedo/workspace/amberdata
COPY . ./
RUN pip install requests numpy pandas matplotlib tqdm python-dotenv xlrd
CMD ["python", "src/main.py"]