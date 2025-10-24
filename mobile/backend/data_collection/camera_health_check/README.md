# Camera Health Check Tool

A tool to systematically test the health and reliability of NYC traffic cameras.

## Overview

This tool performs a two-phase test on all traffic cameras:

### Phase 1: Quick Status Check
- Makes 1 call per camera
- Identifies completely dead cameras
- Runtime: ~3-5 minutes
- Output: Initial dead vs working camera list

### Phase 2: Reliability Test
- Only tests cameras that passed Phase 1
- Makes 5 calls per working camera
- Checks for intermittent failures
- Runtime: ~10-15 minutes
- Output: Detailed reliability scores

## Rate Limiting
- Conservative approach: 1 request per second
- Exponential backoff if rate limited
- Respects server response codes

## Usage
```bash
# Run the full test suite
python test_cameras.py

# View results
cat results/latest_report.json
```

## Output Format
Results are saved in JSON format with:
- Camera ID/Address
- Success rate
- Average response time
- Image validation results
- Any error patterns detected 