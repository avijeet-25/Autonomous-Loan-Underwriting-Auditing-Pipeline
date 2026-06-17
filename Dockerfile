FROM python:3.11-slim


RUN useradd -m -u 1000 user
WORKDIR /home/user/app

RUN chown -R user:user /home/user/app
USER user

COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user:user . .

EXPOSE 7860 8000


RUN chmod +x start.sh


CMD ["sh", "start.sh"]