# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 6900 available to the world outside this container
EXPOSE 6900

# Define environment variables with defaults
ENV ARGILLA_API_KEY=argilla.apikey
ENV ARGILLA_API_URL=http://localhost:6900
ENV MAX_RECORDS=10
ENV LLAMA_MODEL_ID=meta-llama/Meta-Llama-3.1-8B-Instruct
ENV GEMMA_MODEL_ID=google/gemma-1.1-7b-it
ENV ULTRAFEEDBACK_MODEL_ID=meta-llama/Meta-Llama-3.1-70B-Instruct

# Run run.py when the container launches
CMD ["python", "run.py"]