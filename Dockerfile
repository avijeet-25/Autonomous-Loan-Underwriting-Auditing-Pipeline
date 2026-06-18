FROM python:3.11-slim

# 1. Stay as root for system-level installations
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 2. Setup your application user
RUN useradd -m -u 1000 user
WORKDIR /home/user/app
RUN chown -R user:user /home/user/app

# 3. Switch to user for everything else
USER user

# Add this to Dockerfile
ENV PATH="/home/user/.local/bin:${PATH}"

# 4. Copy requirements and install
# We use the build cache mount here to stop the "re-downloading GBs" problem
COPY --chown=user:user requirements.txt .
RUN --mount=type=cache,target=/home/user/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application
COPY --chown=user:user . .

EXPOSE 7860 8000

RUN chmod +x start.sh
CMD ["sh", "start.sh"]