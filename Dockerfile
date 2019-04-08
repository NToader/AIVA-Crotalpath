FROM python:3.7
RUN apt-get update -y && apt-get install -y tesseract-ocr
COPY /requirements.txt AIVA-Crotalpath/requirements.txt
RUN pip3 install -r AIVA-Crotalpath/requirements.txt
COPY / AIVA-Crotalpath/
WORKDIR /AIVA-Crotalpath
EXPOSE 5000
ENTRYPOINT circusd crotalpath.ini