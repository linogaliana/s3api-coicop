FROM ubuntu:22.04
# Install Python
RUN apt-get -y update && \
    apt-get install -y python3-pip
# Install project dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .
CMD ["uvicorn api.main:app --reload --host \"0.0.0.0\" --port 5000"]

