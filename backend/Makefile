list:
	make -qp | awk -F: '/^[a-zA-Z0-9][a-zA-Z0-9_.-]*:/ {print $$1}' | grep -v 'Makefile'

engine-arm:
	DOCKER_BUILDKIT=1 docker buildx build --platform linux/arm64 --progress=plain --file engine.arm64.Dockerfile  -t seclens-engine-arm:0.2 .

engine-amd:
	DOCKER_BUILDKIT=1 docker buildx build --platform linux/amd64 --progress=plain --file engine.amd64.Dockerfile  -t seclens-engine-amd:0.2 .
