# Chromium flags that work locally, in Docker and on AWS Lambda.
# Lambda has no /dev/shm, no GPU, and does not allow the sandbox or zygote processes.
CHROMIUM_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--single-process",
    "--no-zygote",
    "--disable-extensions",
]
