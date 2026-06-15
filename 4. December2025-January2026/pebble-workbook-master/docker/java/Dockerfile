FROM --platform=linux/arm64 eclipse-temurin:17-jdk-jammy

WORKDIR /app

# Install required packages
RUN apt-get update && \
    apt-get install -y wget unzip && \
    rm -rf /var/lib/apt/lists/*

# Download JUnit Platform Console Standalone
RUN wget https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.9.2/junit-platform-console-standalone-1.9.2.jar -O /junit-platform-console-standalone.jar

# The actual solution files will be mounted at runtime
CMD ["sh", "-c", "javac -cp /junit-platform-console-standalone.jar Solution.java Test.java && java -jar /junit-platform-console-standalone.jar --class-path . --scan-class-path"] 