FROM python
FROM mysql

COPY . /src

#CMD ./add_db.sh 

#RUN apt autoremove
RUN apt -y update
#RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pip
RUN apt-get -y install python3-pip
RUN pip3 install gspread
RUN pip3 install pymysql
RUN pip3 install oauth2client
RUN pip3 install sqlalchemy
#RUN pip3 install mysqlclient
RUN cd /src
CMD ["python3", "/src/sync-db.py"]

