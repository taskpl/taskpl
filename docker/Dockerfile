FROM python:3.7-slim

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple .

EXPOSE 9410

CMD [ "python", "docker/entry.py" ]
