# LocalMockr - API Proxy and Mock Testing Suite

A complete local API mocking and proxying toolkit for testing code that depends on external REST APIs.

## Repository Structure

```
AI/
├── README.md
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── localmockr-python/
│   ├── localmockr.py
│   ├── ui.html
│   ├── embed_ui.py
│   ├── run.ps1
│   ├── build.bat
│   ├── build.ps1
│   └── README.md
└── spring-mock-api/
    ├── pom.xml
    ├── run.bat
    ├── build-jar.bat
    ├── mvnw.cmd
    ├── src/main/java/com/localmock/mockapi/
    │   ├── MockApiApplication.java
    │   ├── controller/CustomerController.java
    │   ├── model/BankDetails.java
    │   ├── model/CustomerResponse.java
    │   ├── model/ApiResponse.java
    │   └── config/GlobalExceptionHandler.java
    └── src/main/resources/application.properties
```

## Quick Start

### LocalMockr Python
```bash
cd localmockr-python
python embed_ui.py
python localmockr_embedded.py
```
Open http://localhost:3848 — point your app at http://localhost:3847

### Spring Boot Mock API
```bash
cd spring-mock-api
run.bat
```
Point your app at http://localhost:8081

## Port Reference

| Port | Service |
|------|---------|
| 3847 | LocalMockr proxy |
| 3848 | LocalMockr dashboard |
| 8081 | Spring Boot mock API |

## Licence
MIT
