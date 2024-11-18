# ACMETravel Log Generator

This script generates simulated travel system logs and sends them to Grafana Cloud using the OTLP protocol.

## Setup

1. Set up your environment variables:

```bash
export GRAFANA_INSTANCE_ID='your-instance-id'
export GRAFANA_API_KEY='your-api-key'
```

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
