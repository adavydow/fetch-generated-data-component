FROM python:3.7

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y curl && \
    apt-get clean && \
    rm /var/lib/apt/lists/*_*

# app
RUN mkdir app
WORKDIR app

# SSH
COPY ssh-keys /root/.ssh
RUN chmod 700 /root/.ssh
RUN chmod 600 /root/.ssh/id_rsa
RUN chmod 644 /root/.ssh/id_rsa.pub
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts
RUN chmod 644 /root/.ssh/known_hosts

# install dependencies
RUN mkdir align
COPY fetch_generated_data/__init__.py fetch_generated_data/__init__.py
COPY setup.py setup.py
RUN python setup.py egg_info && \
	pip install --no-cache-dir -r fetch_generated_data.egg-info/requires.txt && \
	rm -r fetch_generated_data.egg-info
RUN rm -r fetch_generated_data

# install package
COPY fetch_generated_data fetch_generated_data
RUN pip install --no-cache-dir .