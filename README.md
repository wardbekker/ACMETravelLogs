# ACMETravel Log Generator

This script generates simulated travel system logs and sends them to Grafana Cloud using the OTLP protocol.

## Setup

You can configure your environment in one of two ways:

### Option 1: Using a .env file (Recommended)

1. Create a `.env` file in the root directory with the following content:

```
GRAFANA_INSTANCE_ID='your-instance-id'
GRAFANA_API_KEY='your-api-key'
OTLP_ENDPOINT='your-otlp-endpoint'
```

The script will automatically load these environment variables when it runs.

### Option 2: Using environment variables directly

Set up your environment variables in your terminal:

```bash
export GRAFANA_INSTANCE_ID='your-instance-id'
export GRAFANA_API_KEY='your-api-key'
```

After configuring your environment using either method:

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Generator

After setting up your environment variables, run the generator:

```bash
python generator.py
```

The script will run indefinitely, generating various types of logs including:
- Normal operation logs
- Minor error logs
- Escalating error patterns

## Environment Variables

- `GRAFANA_INSTANCE_ID`: Your Grafana Cloud instance ID
- `GRAFANA_API_KEY`: Your Grafana Cloud API key
- `OTLP_ENDPOINT`: Your OTLP endpoint URL (optional, defaults to Grafana Cloud endpoint)

These environment variables must be set before running the script. If they are not set, the script will display an error message with instructions.

## Updating Protocol Buffer Code

If you need to update the protocol buffer definitions, follow these steps:

1. Make your changes to the .proto files in their respective directories:
   - `opentelemetry/proto/common/v1/common.proto`
   - `opentelemetry/proto/logs/v1/logs.proto`
   - `opentelemetry/proto/resource/v1/resource.proto`

2. Regenerate the Python code by running:
   ```bash
   python -m grpc_tools.protoc \
     --proto_path=. \
     --python_out=. \
     opentelemetry/proto/common/v1/common.proto \
     opentelemetry/proto/logs/v1/logs.proto \
     opentelemetry/proto/resource/v1/resource.proto
   ```

This will update the corresponding *_pb2.py files with your changes.
