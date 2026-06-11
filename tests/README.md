# 🧪 Brahmakaal API Testing Suite

Comprehensive automated testing framework for the Brahmakaal API with 10 endpoints and advanced features.

## 📋 Overview

This testing suite provides complete validation of:
- **10 API Endpoints** (5 Core + 5 Advanced)
- **Accuracy Validation** against Drik Panchang
- **Performance Benchmarking** 
- **Integration Testing**
- **Error Handling & Edge Cases**

## 🚀 Quick Start

### Run All Tests
```bash
python run_tests.py
```

### Run Quick Smoke Tests
```bash
python run_tests.py --type quick
```

### Run Specific Test Categories
```bash
# Accuracy validation only
python run_tests.py --type accuracy

# Performance tests only  
python run_tests.py --type performance

# Integration tests only
python run_tests.py --type integration
```

## 📂 Test Structure

```
tests/
├── conftest.py                 # Pytest fixtures and configuration
├── pytest.ini                 # Pytest settings
├── api/                        # API endpoint tests
│   ├── test_panchang_api.py   # Core Panchang API tests
│   ├── test_panchaka_api.py   # Enhanced Panchaka tests
│   └── ...                    # Other endpoint tests
├── accuracy/                   # Accuracy validation
│   └── test_drik_panchang_validation.py
├── performance/                # Performance benchmarks
│   └── test_api_performance.py
├── integration/                # End-to-end tests
│   └── test_end_to_end.py
├── unit/                       # Unit tests (future)
└── utils/                      # Test utilities
```

## 🎯 Test Categories

### 1. API Tests (`tests/api/`)
- **Core APIs**: Panchang, Horoscope, Muhurta, Transits, Ayanamsha
- **Advanced APIs**: Panchaka, Lagna, Complete Muhurta, Inauspicious, Calendar
- **Validation**: Request/response structure, data types, error handling
- **Edge Cases**: Invalid inputs, boundary conditions

### 2. Accuracy Tests (`tests/accuracy/`)
- **Drik Panchang Validation**: Compare against known values
- **Cross-Reference Validation**: Multiple source verification
- **Time Accuracy**: Solar/lunar timing precision (±10 minutes)
- **Calculation Accuracy**: Tithi, Nakshatra, planetary positions

### 3. Performance Tests (`tests/performance/`)
- **Response Time Benchmarks**: 
  - Core APIs: <3 seconds
  - Advanced APIs: <100ms
- **Concurrent Load Testing**: Multiple simultaneous requests
- **Memory Stability**: Extended operation testing
- **Cache Effectiveness**: Repeated request optimization

### 4. Integration Tests (`tests/integration/`)
- **End-to-End Workflows**: Complete API interaction chains
- **Cross-Endpoint Consistency**: Data correlation between APIs
- **System Health**: API availability and reliability
- **Error Recovery**: Graceful degradation testing

## 📊 Test Fixtures & Data

### Standard Test Locations
- **Mumbai**: 19.0760°N, 72.8777°E (IST +5:30)
- **Delhi**: 28.6139°N, 77.2090°E (IST +5:30)
- **London**: 51.5074°N, 0.1278°W (GMT +0:00)
- **New York**: 40.7128°N, 74.0060°W (EST -5:00)

### Test Dates
- **Current Test**: 2025-07-25 (Development reference)
- **Solstices**: 2025-06-21, 2025-12-21
- **Lunar Events**: New Moon, Full Moon dates
- **Festival Dates**: Diwali 2025 (approximate)

### Validation Data
- **Drik Panchang Reference**: Mumbai July 25, 2025
- **Expected Values**: Tithi (Pratipada), Nakshatra (Pushya), Solar times
- **Tolerance Levels**: ±10 minutes for times, ±0.01° for coordinates

## ⚡ Performance Benchmarks

| API Endpoint | Target Time | Max Time | Status |
|--------------|-------------|----------|---------|
| **Core Panchang** | 2.0s | 3.0s | ✅ |
| **Enhanced Panchaka** | 0.06s | 0.1s | ✅ |
| **Udaya Lagna** | 0.05s | 0.1s | ✅ |
| **Complete Muhurta** | 0.06s | 0.1s | ✅ |
| **Inauspicious Periods** | 0.05s | 0.1s | ✅ |
| **Calendar Systems** | 0.03s | 0.1s | ✅ |

## 🔧 Test Configuration

### Pytest Markers
```bash
# Run only fast tests
pytest -m "not slow"

# Run accuracy tests only
pytest -m accuracy

# Run performance tests only  
pytest -m performance

# Run integration tests only
pytest -m integration
```

### Coverage Reporting
```bash
# Generate HTML coverage report
python run_tests.py --coverage

# View coverage in browser
open htmlcov/index.html
```

## 📈 Usage Examples

### Basic API Testing
```bash
# Test all endpoints
pytest tests/api/ -v

# Test specific endpoint
pytest tests/api/test_panchang_api.py -v

# Test with coverage
pytest tests/api/ --cov=kaal_engine --cov-report=html
```

### Accuracy Validation
```bash
# Validate against Drik Panchang
pytest tests/accuracy/ -v -m accuracy

# Check specific location accuracy
pytest tests/accuracy/test_drik_panchang_validation.py::test_mumbai_july_25_2025_accuracy -v
```

### Performance Monitoring
```bash
# Run performance benchmarks
pytest tests/performance/ -v -m performance

# Extended load testing
pytest tests/performance/ -v -m "performance and slow"
```

## 🛠 Advanced Usage

### Parallel Execution
```bash
# Install parallel testing
pip install pytest-xdist

# Run tests in parallel
pytest -n auto tests/
```

### Custom Test Selection
```bash
# Run tests matching pattern
pytest -k "panchang" -v

# Run tests by file pattern
pytest tests/api/test_*api.py -v

# Skip slow tests
pytest -m "not slow" -v
```

### Debugging Tests
```bash
# Stop on first failure
pytest -x tests/

# Verbose output with full tracebacks
pytest -vvv --tb=long tests/

# Drop into debugger on failure
pytest --pdb tests/
```

## 📋 Test Dependencies

```bash
# Core testing
pytest>=7.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0

# Coverage and reporting
pytest-cov>=4.0.0
coverage>=7.0.0

# Performance and utilities
pytest-timeout>=2.1.0
pytest-xdist>=3.0.0
```

## 🎯 Quality Metrics

### Success Criteria
- **API Tests**: 100% endpoint coverage
- **Accuracy Tests**: <10 minute time difference vs Drik Panchang
- **Performance Tests**: All endpoints within benchmark limits
- **Integration Tests**: Complete workflow validation
- **Coverage**: >80% code coverage

### Test Execution Targets
- **Quick Tests**: <30 seconds
- **Full Suite**: <10 minutes  
- **Extended Tests**: <30 minutes
- **Success Rate**: >95% pass rate

## 🔍 Troubleshooting

### Common Issues
1. **Server Not Running**: Ensure API server is started before testing
2. **Import Errors**: Check Python path and dependencies
3. **Timeout Errors**: Increase timeout values for slow systems
4. **Rate Limiting**: Reduce concurrent test execution

### Debug Commands
```bash
# Check test discovery
pytest --collect-only tests/

# Validate test configuration
pytest --markers

# Test specific fixture
pytest --fixtures -v
```

## 📞 Support

For testing issues or improvements:
1. Check test logs in `test-results.xml`
2. Review coverage reports in `htmlcov/`
3. Run individual test files for isolation
4. Verify API server health with `curl localhost:8000/health` 