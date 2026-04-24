![alt text](block_diagram.png)

This is the architecture of the framework


KEY DESIGN DECISIONS
===============================================================================
  1) Configuration via .env
     - All environment-specific values (URLs, credentials, timeouts) live in a .env file, loaded by python-dotenv.
     - .env.example is committed as a template; .env is gitignored.
     - This allows the same code to run in different environments (CI/CD nightly,local dev) by simply swapping the .env file.

  2) Retry with Exponential Backoff
     - Network calls are wrapped with a @retry decorator (utils/retry_decorator.py)to handle transient failures — critical for IoT devices on unreliable networks.

  3) Mocked Unit Tests + Real Integration Tests
     - Default test run: all API calls are mocked (pytest-mock) so tests are fast, deterministic, and runnable without hardware.
     - CI/CD nightly run: tests marked @pytest.mark.real can be executed with --real flag against the actual device (192.168.0.2) and cloud(https://automation.ienso.com) after firmware/cloud deployment.

  4) Allure Reporting
     - pytest --alluredir=allure-results generates rich reports for the nightly
       CI/CD pipeline.

 CONSIDERATIONS & POTENTIAL PITFALLS
================================================================================
  1) Network Reliability
     - The device is on a local network (192.168.0.2). Flaky Wi-Fi or network partitions can cause intermittent test failures.
     - Mitigation: Retry decorator with exponential backoff, configurable timeout via .env.
     
  2) Firmware Update Timing
     - After flashing new firmware, the device needs time to boot and become reachable.
     - Mitigation: CI/CD should include a health-check wait step before running tests (e.g. poll GET /api/device/name until 200).
     
  3) Cloud Deployment Propagation
     - Newly deployed cloud services may take time to become fully available.
     - Mitigation: same health-check polling approach.
     
  4) Test Isolation
     - The device name is shared state. Tests that modify it can interfere with each other if run in parallel.
     - Mitigation: tests reset state in setup/teardown, avoid pytest-xdist parallelism for integration tests against real hardware.
     
  5) Token Expiry
     - If the test suite takes a long time, tokens may expire mid-run.
     - Mitigation: AuthService supports force_refresh; tests can catch 401 and re-authenticate.
     
  6) Security
     - Credentials must never be committed to version control.
     - Mitigation: .env is gitignored; CI/CD injects secrets via environment variables.
