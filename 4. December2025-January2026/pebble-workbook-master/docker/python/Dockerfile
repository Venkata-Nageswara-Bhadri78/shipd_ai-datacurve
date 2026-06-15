FROM --platform=linux/arm64 python:3.11-slim

WORKDIR /app

# Install pytest
RUN pip install pytest pytest-timeout

# Run tests when container starts
CMD ["pytest", "-v", "--timeout=5"] 