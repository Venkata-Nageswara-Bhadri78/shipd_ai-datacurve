FROM --platform=linux/arm64 gcc:12.4

WORKDIR /app

# Install required packages
RUN apt-get update && \
    apt-get install -y \
    cmake \
    libgtest-dev \
    && rm -rf /var/lib/apt/lists/*

# Build and install GTest
RUN cd /usr/src/gtest && \
    cmake CMakeLists.txt && \
    make && \
    cp lib/*.a /usr/lib

# The actual solution files will be mounted at runtime
CMD ["sh", "-c", "g++ -std=c++17 solution.cpp test.cpp -o test -lgtest -lgtest_main -pthread && ./test"] 