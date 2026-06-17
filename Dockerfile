FROM python:3.11-slim


RUN useradd -m -u 1000 user
WORKDIR /home/user/app

COPY --chown=user:user . .

RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 7860


RUN chmod +x start.sh

# ALWAYS AT THE VERY BOTTOM
CMD ["sh", "start.sh"]