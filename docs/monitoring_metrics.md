# Monitoring and Metrics Reference

## Metric Types

### 1. System Metrics
- `system.cpu.percent`: CPU utilization percentage
- `system.memory.percent`: Memory utilization percentage 
- `system.memory.used`: Used memory in bytes
- `system.memory.available`: Available memory in bytes
- `system.disk.percent`: Disk utilization percentage
- `system.disk.used`: Used disk space in bytes
- `system.disk.free`: Free disk space in bytes

### 2. API Metrics
- `api.request.duration`: Request processing time (seconds)
- `api.requests.total`: Total request count
- `api.requests.success`: Successful request count
- `api.requests.error`: Failed request count
- `api.latency`: API endpoint latency

### 3. Validation Metrics
- `validation.duration`: Email validation duration
- `validation.count`: Validation attempt count
- `validation.success_rate`: Validation success percentage
- `dns.lookup.duration`: DNS lookup timing
- `smtp.check.duration`: SMTP verification timing

### 4. Cache Metrics
- `cache.hits`: Cache hit count
- `cache.misses`: Cache miss count
- `cache.size`: Current cache size
- `cache.hit_rate`: Cache hit rate percentage

### 5. Error Metrics
- `errors.<type>`: Error count by type
- Error types include:
  - http_error
  - validation_error
  - service_error
  - system_error

## Tags

Common tags used across metrics:

1. **API Tags**
   - endpoint: API endpoint path
   - method: HTTP method
   - status_code: Response status code

2. **Validation Tags**
   - validation_type: Type of validation
   - status: success/failure
   - provider: External service provider

3. **Error Tags**
   - error_type: Category of error
   - severity: Error severity level
   - component: System component

4. **Resource Tags**
   - resource_type: Type of resource
   - instance: Server instance ID
   - region: Deployment region