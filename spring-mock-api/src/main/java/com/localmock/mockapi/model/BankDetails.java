package com.localmock.mockapi.model;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class BankDetails {
    private String accountHolderName, accountNumber, routingNumber, bankName, bankCode;
    private String accountType, currency, country, iban, swiftCode, branchCode, branchName;
    private boolean verified, primary;
    private String verifiedAt;

    private BankDetails() {}

    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private final BankDetails obj = new BankDetails();
        public Builder accountHolderName(String v) { obj.accountHolderName = v; return this; }
        public Builder accountNumber(String v)      { obj.accountNumber = v;      return this; }
        public Builder routingNumber(String v)      { obj.routingNumber = v;      return this; }
        public Builder bankName(String v)           { obj.bankName = v;           return this; }
        public Builder bankCode(String v)           { obj.bankCode = v;           return this; }
        public Builder accountType(String v)        { obj.accountType = v;        return this; }
        public Builder currency(String v)           { obj.currency = v;           return this; }
        public Builder country(String v)            { obj.country = v;            return this; }
        public Builder iban(String v)               { obj.iban = v;               return this; }
        public Builder swiftCode(String v)          { obj.swiftCode = v;          return this; }
        public Builder branchCode(String v)         { obj.branchCode = v;         return this; }
        public Builder branchName(String v)         { obj.branchName = v;         return this; }
        public Builder verified(boolean v)          { obj.verified = v;           return this; }
        public Builder verifiedAt(String v)         { obj.verifiedAt = v;         return this; }
        public Builder primary(boolean v)           { obj.primary = v;            return this; }
        public BankDetails build()                  { return obj; }
    }

    public String getAccountHolderName() { return accountHolderName; }
    public String getAccountNumber()     { return accountNumber; }
    public String getRoutingNumber()     { return routingNumber; }
    public String getBankName()          { return bankName; }
    public String getBankCode()          { return bankCode; }
    public String getAccountType()       { return accountType; }
    public String getCurrency()          { return currency; }
    public String getCountry()           { return country; }
    public String getIban()              { return iban; }
    public String getSwiftCode()         { return swiftCode; }
    public String getBranchCode()        { return branchCode; }
    public String getBranchName()        { return branchName; }
    public boolean isVerified()          { return verified; }
    public String getVerifiedAt()        { return verifiedAt; }
    public boolean isPrimary()           { return primary; }
}
