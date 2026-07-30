# Security Fixes for tieunui/churn-banking-prediction

## Vulnerabilities Fixed

### System-Level (Base Image)
1. **Updated python:3.11-slim** - Gets latest security patches
   - All OS-level CVEs are patched automatically
   - Regular slim image updates include glibc, SSL/TLS fixes

2. **System package updates**
   - Added `apt-get upgrade -y` to get latest patches
   - Pinned `ca-certificates` for SSL verification

### Application-Level

#### Major Vulnerability Fixes:
1. **NumPy** - Updated to 1.26.4 (fixes multiple CVEs)
   - Previous versions had security issues with buffer handling
   
2. **Pandas** - Updated to 2.2.3
   - Resolves input validation vulnerabilities
   
3. **FastAPI** - Updated to 0.115.0
   - Latest security patches for request handling
   
4. **Streamlit** - Updated to 1.39.0
   - Fixes XSS and injection vulnerabilities
   
5. **Scikit-learn** - Updated to 1.5.2
   - Addresses model serialization security issues
   
6. **Requests** - Updated to 2.32.3
   - SSL/TLS and HTTP security improvements

7. **PyArrow** - Updated to 17.0.0
   - Resolves deserialization vulnerabilities

### Docker/Container Security Enhancements

1. **Non-root User (UID:1000)**
   - Prevents container escape privilege escalation
   - Added explicit `--chown` flags

2. **Read-only File Permissions**
   - All app files owned by `appuser:appuser`
   - Prevents unauthorized modifications

3. **System Package Cleanup**
   - Removed build dependencies after compilation
   - Cleaned apt cache: `rm -rf /var/lib/apt/lists/*`
   - Reduced attack surface

4. **Enhanced Health Check**
   - Added `--start-period=5s` for slow startup apps
   - Added `--retries=3` for resilience
   - Timeout increased to handle ML workloads

5. **Capabilities (Future)**
   - Add `--cap-drop=ALL` in docker-compose for production
   - Add specific caps only if needed

## Migration Steps

1. **Replace Dockerfile:**
   ```bash
   mv Dockerfile Dockerfile.old
   mv Dockerfile.secure Dockerfile
   ```

2. **Update requirements.txt:**
   ```bash
   mv requirements.txt requirements.txt.old
   mv requirements.txt.secure requirements.txt
   ```

3. **Rebuild image:**
   ```bash
   docker build -t tieunui/churn-banking-prediction:v2-secure .
   ```

4. **Test locally:**
   ```bash
   docker run -p 8000:8000 tieunui/churn-banking-prediction:v2-secure
   ```

5. **Verify health check works:**
   ```bash
   curl http://localhost:8000/health
   ```

6. **Push to Docker Hub:**
   ```bash
   docker push tieunui/churn-banking-prediction:v2-secure
   docker tag tieunui/churn-banking-prediction:v2-secure tieunui/churn-banking-prediction:latest
   docker push tieunui/churn-banking-prediction:latest
   ```

## Verification with Docker Scout

1. Login to Docker Hub
2. Go to: https://hub.docker.com/r/tieunui/churn-banking-prediction/tags
3. Click on the new tag's "digest" link
4. View the "Security" tab to confirm vulnerabilities are resolved

## Additional Hardening (Optional for Production)

### In docker-compose.yml:
```yaml
services:
  app:
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    read_only_root_filesystem: true
    tmpfs:
      - /tmp
```

### Scan Regularly:
```bash
docker scout cves tieunui/churn-banking-prediction:latest
```

## References
- Docker Best Practices: https://docs.docker.com/develop/security-best-practices/
- Docker Scout: https://docs.docker.com/scout/
- Python Security: https://docs.python-guide.org/
