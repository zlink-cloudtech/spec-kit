# Quickstart: Release Server

## Building the Server

```bash
cd release-server
docker build -t spec-kit/release-server .
```

## Running Locally

Create a data directory:
```bash
mkdir -p data
```

Run the container:
```bash
docker run -p 8000:8000 \
  -v $(pwd)/data:/data \
  -e MAX_PACKAGES=5 \
  -e AUTH_TOKEN=secret123 \
  spec-kit/release-server
```

## Usage

### 1. Upload a Package

```bash
# Upload a dummy file
echo "content" > spec-kit-template-dummy-sh.zip
curl -X POST -H "Authorization: Bearer secret123" -F "file=@spec-kit-template-dummy-sh.zip" http://localhost:8000/upload
```

### 2. Verify Listing

Visit `http://localhost:8000/packages` in your browser.

### 3. Use with Specify CLI

```bash
specify init my-project --template-url http://localhost:8000/latest --ai dummy --script sh
```

### 4. Overwrite a Package

```bash
curl -X POST -H "Authorization: Bearer secret123" -F "file=@spec-kit-template-dummy-sh.zip" "http://localhost:8000/upload?overwrite=true"
```

### 5. Delete a Package

Using script:
```bash
./release-server/scripts/delete.sh -t secret123 spec-kit-template-dummy-sh.zip
```

Using curl directly:
```bash
curl -X DELETE -H "Authorization: Bearer secret123" "http://localhost:8000/assets/spec-kit-template-dummy-sh.zip"
```
