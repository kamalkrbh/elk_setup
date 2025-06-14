FROM ubuntu:22.04

# Install Filebeat
RUN apt-get update && \
    apt-get install -y curl && \
    curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-9.0.0-amd64.deb && \
    dpkg -i filebeat-9.0.0-amd64.deb && \
    rm filebeat-9.0.0-amd64.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Basic Filebeat configuration (adjust as needed)
COPY filebeat.yml /etc/filebeat/filebeat.yml

# Attempt to setup dashboards and then start Filebeat in the foreground.
# The `filebeat setup` command relies on Elasticsearch and Kibana being available.
# `depends_on` in docker-compose helps, but services might not be fully ready.
# If `filebeat setup` fails, Filebeat will not start due to `&&`.
#CMD ["sh", "-c", "filebeat setup -e --dashboards && exec filebeat -e -c /etc/filebeat/filebeat.yml"]

CMD ["filebeat", "-e"]