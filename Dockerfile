FROM python:3.9

#RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Create a user and set up workspace
RUN groupadd -g 1000 devuser && \
    useradd -m -u 1000 -g devuser devuser && \
    mkdir -p /home/devuser/workspace && \
    chown devuser:devuser /home/devuser/workspace

USER devuser

WORKDIR /home/devuser/workspace

# Install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

EXPOSE 8000

CMD ["python", "main.py"]