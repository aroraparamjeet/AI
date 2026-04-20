package com.localmock.mockapi.controller;

import com.localmock.mockapi.model.ApiResponse;
import com.localmock.mockapi.model.BankDetails;
import com.localmock.mockapi.model.CustomerResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/customer")
@CrossOrigin(origins = "*")
public class CustomerController {

    private static final Logger log = LoggerFactory.getLogger(CustomerController.class);

    @GetMapping("/bankdetails")
    public ResponseEntity<CustomerResponse> getBankDetails(
            @RequestParam(required = false, defaultValue = "CUST-MOCK-001") String customerId) {

        log.info("[MOCK] GET /api/customer/bankdetails  customerId={}", customerId);

        CustomerResponse response = CustomerResponse.builder()
                .source("LOCAL_MOCK")
                .environment("mock")
                .warning("This response is served by the local Spring Boot mock server - NOT the real API")
                .customerId(customerId)
                .requestId("MOCK-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase())
                .retrievedAt(Instant.now().toString())
                .bankDetails(BankDetails.builder()
                        .accountHolderName("MOCK - John Smith")
                        .accountNumber("****MOCK")
                        .routingNumber("000000000")
                        .bankName("MOCK Bank")
                        .bankCode("MOCKBANK")
                        .accountType("CHECKING")
                        .currency("USD")
                        .country("US")
                        .iban("MOCK-IBAN-001")
                        .swiftCode("MOCKSWIFT")
                        .verified(true)
                        .verifiedAt("2024-01-01T00:00:00Z")
                        .primary(true)
                        .build())
                .linkedAccounts(List.of(
                        Map.of("accountId", "MOCK-ACC-001", "bankName", "MOCK Savings Bank",
                               "accountNumber", "****MOCK", "accountType", "SAVINGS",
                               "currency", "USD", "primary", false, "verified", true)
                ))
                .paymentMethods(Map.of("directDebit", true, "wireTransfer", true,
                                       "achTransfer", true, "internationalWire", false))
                .limits(Map.of("dailyTransferLimit", 99999.99, "monthlyTransferLimit", 99999.99, "currency", "USD"))
                .mock(Map.of("servedBy", "Spring Boot LocalMock", "port", "8081",
                             "note", "Replace http://localhost:8081 with the real API base URL when ready"))
                .build();

        return ResponseEntity.ok(response);
    }

    @GetMapping("/bankdetails/{accountId}")
    public ResponseEntity<Object> getBankDetailById(@PathVariable String accountId) {
        log.info("[MOCK] GET /api/customer/bankdetails/{}", accountId);

        if ("NOTFOUND".equalsIgnoreCase(accountId)) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ApiResponse.error("NOT_FOUND", "No bank account found with id: " + accountId, "LOCAL_MOCK"));
        }
        if ("FORBIDDEN".equalsIgnoreCase(accountId)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(ApiResponse.error("FORBIDDEN", "You do not have permission to view this account", "LOCAL_MOCK"));
        }

        BankDetails details = BankDetails.builder()
                .accountHolderName("MOCK - Jane Doe")
                .accountNumber("****" + accountId.substring(0, Math.min(4, accountId.length())).toUpperCase())
                .routingNumber("000000000").bankName("MOCK Bank").bankCode("MOCKBANK")
                .accountType("SAVINGS").currency("USD").country("US")
                .iban("MOCK-IBAN-" + accountId).swiftCode("MOCKSWIFT")
                .verified(true).verifiedAt("2024-01-01T00:00:00Z").primary(false).build();

        return ResponseEntity.ok(Map.of(
                "source", "LOCAL_MOCK", "environment", "mock",
                "warning", "This is a mock response from the local Spring Boot server",
                "accountId", accountId, "retrievedAt", Instant.now().toString(),
                "requestId", "MOCK-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase(),
                "bankDetails", details,
                "_mock", Map.of("servedBy", "Spring Boot LocalMock", "port", "8081")
        ));
    }

    @PostMapping("/bankdetails")
    public ResponseEntity<Object> createBankDetail(@RequestBody Map<String, Object> requestBody) {
        log.info("[MOCK] POST /api/customer/bankdetails  body={}", requestBody);
        String newId = "MOCK-NEW-" + UUID.randomUUID().toString().substring(0, 6).toUpperCase();
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                "source", "LOCAL_MOCK", "environment", "mock",
                "warning", "This is a mock response - no real data was created",
                "status", "CREATED", "accountId", newId,
                "createdAt", Instant.now().toString(),
                "requestId", "MOCK-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase(),
                "receivedPayload", requestBody,
                "_mock", Map.of("servedBy", "Spring Boot LocalMock", "note", "Nothing was actually saved")
        ));
    }

    @DeleteMapping("/bankdetails/{accountId}")
    public ResponseEntity<Object> deleteBankDetail(@PathVariable String accountId) {
        log.info("[MOCK] DELETE /api/customer/bankdetails/{}", accountId);
        return ResponseEntity.ok(Map.of(
                "source", "LOCAL_MOCK", "environment", "mock",
                "warning", "This is a mock response - nothing was actually deleted",
                "status", "DELETED", "accountId", accountId,
                "deletedAt", Instant.now().toString(),
                "_mock", Map.of("servedBy", "Spring Boot LocalMock", "port", "8081")
        ));
    }

    @GetMapping("/health")
    public ResponseEntity<Object> health() {
        return ResponseEntity.ok(Map.of(
                "status", "UP", "service", "Spring Boot LocalMock API",
                "port", 8081, "time", Instant.now().toString(),
                "message", "Mock server is running and ready"
        ));
    }
}
