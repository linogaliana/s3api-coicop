FROM inseefrlab/onyxia-python-minimal:py3.10.9

# set current work dir
WORKDIR /formation-mlops

# copy project files to the image
COPY --chown=${USERNAME}:${GROUPNAME} . .

# install all the requirements and import corpus
COPY requirements.txt .
COPY main.py .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

# launch the unicorn server to run the api
EXPOSE 8000
CMD ["uvicorn", "main:app",  "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]

