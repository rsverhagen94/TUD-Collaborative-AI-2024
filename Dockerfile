FROM python:3.9.18

WORKDIR /code

# Install dependencies
COPY ./requirements.txt /code/
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application code into the container
COPY . /code/

EXPOSE 3001

CMD ["python", "main.py"]