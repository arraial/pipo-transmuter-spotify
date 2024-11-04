variable "DEFAULT_TAG" {
  default = "pipo_transmuter_spotify:local"
}

target "docker-metadata-action" {
  tags = ["${DEFAULT_TAG}"]
}

group "default" {
  targets = ["image-local"]
}

target "image" {
  inherits = ["docker-metadata-action"]
}

target "image-local" {
  inherits = ["image"]
  output = ["type=docker"]
}

target "image-all" {
  inherits = ["image"]
  platforms = [
    "linux/amd64",
    "linux/arm64"
  ]
}
