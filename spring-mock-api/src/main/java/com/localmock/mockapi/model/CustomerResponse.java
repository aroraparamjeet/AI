package com.localmock.mockapi.model;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.util.List;
import java.util.Map;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class CustomerResponse {
    private String source, environment, warning, customerId, requestId, retrievedAt;
    private BankDetails bankDetails;
    private List<Map<String, Object>> linkedAccounts;
    private Map<String, Object> paymentMethods, limits, mock;

    private CustomerResponse() {}
    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private final CustomerResponse obj = new CustomerResponse();
        public Builder source(String v)                           { obj.source = v;           return this; }
        public Builder environment(String v)                      { obj.environment = v;      return this; }
        public Builder warning(String v)                          { obj.warning = v;          return this; }
        public Builder customerId(String v)                       { obj.customerId = v;       return this; }
        public Builder requestId(String v)                        { obj.requestId = v;        return this; }
        public Builder retrievedAt(String v)                      { obj.retrievedAt = v;      return this; }
        public Builder bankDetails(BankDetails v)                 { obj.bankDetails = v;      return this; }
        public Builder linkedAccounts(List<Map<String,Object>> v) { obj.linkedAccounts = v;   return this; }
        public Builder paymentMethods(Map<String,Object> v)       { obj.paymentMethods = v;   return this; }
        public Builder limits(Map<String,Object> v)               { obj.limits = v;           return this; }
        public Builder mock(Map<String,Object> v)                 { obj.mock = v;             return this; }
        public CustomerResponse build()                           { return obj; }
    }

    public String getSource()                           { return source; }
    public String getEnvironment()                      { return environment; }
    public String getWarning()                          { return warning; }
    public String getCustomerId()                       { return customerId; }
    public String getRequestId()                        { return requestId; }
    public String getRetrievedAt()                      { return retrievedAt; }
    public BankDetails getBankDetails()                 { return bankDetails; }
    public List<Map<String,Object>> getLinkedAccounts() { return linkedAccounts; }
    public Map<String,Object> getPaymentMethods()       { return paymentMethods; }
    public Map<String,Object> getLimits()               { return limits; }
    public Map<String,Object> getMock()                 { return mock; }
}
