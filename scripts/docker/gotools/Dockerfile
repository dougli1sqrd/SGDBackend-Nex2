FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
    apache2 \
    libapache2-mod-wsgi-py3 \
    net-tools \
    python3-pip \
    wget \
    gcc \
    make \
    build-essential
    
RUN cd /var/www && mkdir bin data lib logs tmp FlaskApp && cd FlaskApp && \
    mkdir FlaskApp && cd FlaskApp && mkdir venv static templates

RUN pip3 install Flask && pip3 install -U flask-cors 

COPY www /var/www/
COPY FlaskApp.conf /etc/apache2/sites-available/



### GO Term Finder/Mapper related Perl modules here ###
### ask Matt for list ###



RUN a2enmod wsgi && a2ensite FlaskApp && a2dissite 000-default

RUN pip3 install virtualenv 

RUN cd /var/www/FlaskApp/FlaskApp && virtualenv venv

RUN #!/bin/bash . venv/bin/activate

CMD ["apachectl", "-D", "FOREGROUND"]
