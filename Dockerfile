FROM python
FROM mysql

COPY . /src

RUN apt update --yes
RUN apt install python3-pip --yes
RUN pip3 install gspread
RUN pip3 install pymysql
RUN pip3 install oauth2client
RUN pip3 install sqlalchemy
RUN cd /src
CMD ["python3", "/src/sync-db.py"]

