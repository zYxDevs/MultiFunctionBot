# Pull the Official MFBot Image from the Github Docker Registry
FROM missemily22/multifbot:latest

# Set the working directory
WORKDIR /usr/src/app

# Give read, write, and execute permissions to all users for the working directory
RUN chmod 777 /usr/src/app

# Copy the requirements file
COPY requirements.txt requirements.txt

# Install the requirements
RUN pip3 install --no-cache-dir -r requirements.txt

# Setup and Install Chromium - Playwright on the Server
RUN playwright install chromium
RUN playwright install-deps

# Copy the rest of the files to the working directory
COPY . .

# Give permission to all users to operate the upload module
RUN chmod 777 ./upload_module_x64

# Run the start.sh script
CMD ["bash","start.sh"]