#!/bin/bash
set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
REGISTRY="docker.io"
NAMESPACE="tieunui"
IMAGE="churn-banking-prediction"
NEW_TAG="v2-secure"

echo -e "${YELLOW}🔒 Building Secure Docker Image${NC}"
echo "Registry: $REGISTRY"
echo "Image: $NAMESPACE/$IMAGE:$NEW_TAG"
echo ""

# Step 1: Replace files
echo -e "${YELLOW}📝 Preparing Dockerfile and requirements.txt...${NC}"
[ -f Dockerfile ] && cp Dockerfile Dockerfile.backup.$(date +%s)
[ -f requirements.txt ] && cp requirements.txt requirements.txt.backup.$(date +%s)
cp Dockerfile.secure Dockerfile
cp requirements.txt.secure requirements.txt
echo -e "${GREEN}✓ Files ready${NC}"

# Step 2: Build image
echo -e "${YELLOW}🏗️  Building image...${NC}"
docker build -t $NAMESPACE/$IMAGE:$NEW_TAG .
echo -e "${GREEN}✓ Build complete${NC}"

# Step 3: Test image locally
echo -e "${YELLOW}🧪 Testing image (30 sec health check)...${NC}"
CID=$(docker run -d -p 8000:8000 $NAMESPACE/$IMAGE:$NEW_TAG)
sleep 5
if docker exec $CID curl -f http://localhost:8000/health &>/dev/null; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
    docker logs $CID
    docker stop $CID
    exit 1
fi
docker stop $CID

# Step 4: Scan with Docker Scout
echo -e "${YELLOW}🛡️  Scanning with Docker Scout...${NC}"
docker scout cves $NAMESPACE/$IMAGE:$NEW_TAG 2>/dev/null || echo "(Scout may need login)"

# Step 5: Push to registry
echo -e "${YELLOW}📤 Pushing to Docker Hub...${NC}"
docker push $NAMESPACE/$IMAGE:$NEW_TAG
docker tag $NAMESPACE/$IMAGE:$NEW_TAG $NAMESPACE/$IMAGE:latest
docker push $NAMESPACE/$IMAGE:latest
echo -e "${GREEN}✓ Push complete${NC}"

echo ""
echo -e "${GREEN}✅ Security update complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Verify on Docker Hub: https://hub.docker.com/r/$NAMESPACE/$IMAGE/tags"
echo "2. Check Security tab for vulnerability status"
echo "3. Update any deployments to use the new 'latest' tag"
