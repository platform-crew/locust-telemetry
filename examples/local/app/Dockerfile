FROM locustio/locust:2.37.14

# Set working directories
ENV HOME=/loadtesting
ENV APP_DIR=$HOME/locustapp

# Switch to root to install dependencies
USER root

# Install dependencies and AWS CLI v2
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl unzip groff less \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o /tmp/awscliv2.zip \
    && unzip /tmp/awscliv2.zip -d /tmp \
    && /tmp/aws/install \
    && rm -rf /tmp/awscliv2.zip /tmp/aws \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Switch back to non-root user
USER locust

# Set working directory
WORKDIR $HOME

# Copy the rest of the application code
COPY app/ $APP_DIR

COPY dist/locust_telemetry-0.0.0-py3-none-any.whl $APP_DIR

# Install Python dependencies without cache to reduce layer size
RUN pip install --no-cache-dir -r $APP_DIR/requirements.txt

RUN pip install $APP_DIR/locust_telemetry-0.0.0-py3-none-any.whl
