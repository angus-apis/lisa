# LISA

Logging, information & system analysis

## App structure
```
/LISA
|-- app/                   # Core application code
|-- config/                # Application config
    |-- services.yaml      # A list of services to monitor
|-- images/                # Directory of images
|-- spec/                  # Directory of specification files, including OpenAPI documents etc
|-- tests/                 # Application tests and dummy servers
```

## Services.yaml

The `config/services.yaml` file is used to define services that LISA should monitor. The structure of the file is explained below...

```yaml
microservices:
  - name: User Service  # The display name of the microservice
    id: user_service # Unique slug for the service
    description: Handles user data and authentication  # Brief description of the service
    health_check_url: http://user-service/health  # URL to check the health of the service
    version_url: http://user-service/version  # URL to check the version of the service
```

## Badges

The status of services can be returned as SVG badges, using the endpoint `"/badge/{service_id}"`

<table style="width:100%;">
    <tr>
        <th>Status</th>
        <th>Description</th>
        <th>Badge Image</th>
    </tr>
    <tr>
        <td>UP</td>
        <td>The service is operating normally.</td>
        <td><img src="/images/up.svg" alt="UP Badge"></td>
    </tr>
    <tr>
        <td>DOWN</td>
        <td>The service is not reachable.</td>
        <td><img src="/images/down.svg" alt="DOWN Badge"></td>
    </tr>
    <tr>
        <td>DODGY</td>
        <td>The service is taking longer than usual to respond</td>
        <td><img src="/images/dodgy.svg" alt="DODGY Badge"></td>
    </tr>
    <tr>
        <td>MYSTERY</td>
        <td>Status is not determined.</td>
        <td><img src="/images/mystery.svg" alt="Unknown Badge"></td>
    </tr>
</table>

## OpenAPI spec

In `spec/openapi.yaml` is a file which defines how the microservice endpoints should work. This is currently a work in progress and is not yet complete.

##  Dummy Servers

The `tests/dummies` package contains two dummy servers that can be used to test the application. They are both configured with a version and health endpoint to run on ports `5001` and `5002`

### Run the dummy servers

#### Service A
```bash
.venv/bin/python tests/dummies/service_a.py
```

#### Service B
```bash
.venv/bin/python tests/dummies/service_b.py
```