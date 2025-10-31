FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV PATH=${PATH}:${ANDROID_SDK_ROOT}/cmdline-tools/latest/bin:${ANDROID_SDK_ROOT}/platform-tools

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    wget \
    unzip \
    openjdk-11-jdk \
    zip \
    libncurses5 \
    libtinfo5 \
    && rm -rf /var/lib/apt/lists/*

# Install buildozer
RUN pip3 install --no-cache-dir buildozer Cython==0.29.33

# Create working directory
WORKDIR /app

# Copy project files
COPY . .

# Create buildozer.spec if it doesn't exist
RUN if [ ! -f buildozer.spec ]; then buildozer init; fi

# Build the APK
CMD ["buildozer", "android", "debug"]