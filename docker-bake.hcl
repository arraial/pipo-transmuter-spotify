variable "IMAGE" {
  default = "pipo_transmuter_spotify"
}

variable "PYTHON_VERSION" {
  default = "3.11.10"
}

variable "POETRY_VERSION" {
  default = "1.8.4"
}

variable "TAG" {
  default = "0.0.0"
}

variable "GITHUB_REPOSITORY_OWNER" {
  default = "arraial"
}

target "_common" {
  args = {
    PROGRAM_VERSION = TAG
    PYTHON_VERSION = PYTHON_VERSION
    POETRY_VERSION = POETRY_VERSION
    BUILDKIT_CONTEXT_KEEP_GIT_DIR = 1
  }
  tags = [
    "${GITHUB_REPOSITORY_OWNER}/${IMAGE}:${TAG}",
    "${GITHUB_REPOSITORY_OWNER}/${IMAGE}:latest"
  ]
  labels = {
    "org.opencontainers.image.version" = "${TAG}"
    "org.opencontainers.image.authors" = "https://github.com/${GITHUB_REPOSITORY_OWNER}"
    "org.opencontainers.image.source" = "https://github.com/${GITHUB_REPOSITORY_OWNER}/pipo-transmuter-youtube"
  }
}

target "docker-metadata-action" {}

group "default" {
  targets = ["image"]
}

target "image-local" {
  inherits = ["_common"]
  context = "."
  dockerfile = "Dockerfile"
  output = ["type=docker"]
}

target "test" {
  target = "test"
  inherits = ["image-local"]
  output = ["type=cacheonly"]
}

target "image" {
  inherits = ["image-local", "docker-metadata-action"]
  output = ["type=registry"]
  cache-from = ["type=registry,ref=${GITHUB_REPOSITORY_OWNER}/${IMAGE}:buildcache"]
  cache-to = ["type=registry,ref=${GITHUB_REPOSITORY_OWNER}/${IMAGE}:buildcache,mode=max,image-manifest=true"]
}

target "image-all" {
  inherits = ["image"]
  sbom = true
  output = ["type=registry"]
  platforms = [
   "linux/amd64",
   "linux/arm64"
  ]
}
