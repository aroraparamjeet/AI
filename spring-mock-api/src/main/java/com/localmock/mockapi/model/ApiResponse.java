package com.localmock.mockapi.model;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.time.Instant;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse {

    private String source, environment, status, code, message, timestamp;

    private ApiResponse() {}

    public static ApiResponse error(String code, String message, String source) {
        ApiResponse r = new ApiResponse();
        r.source      = source;
        r.environment = "mock";
        r.status      = "error";
        r.code        = code;
        r.message     = message;
        r.timestamp   = Instant.now().toString();
        return r;
    }

    public static ApiResponse success(String message) {
        ApiResponse r = new ApiResponse();
        r.source      = "LOCAL_MOCK";
        r.environment = "mock";
        r.status      = "success";
        r.message     = message;
        r.timestamp   = Instant.now().toString();
        return r;
    }

    public String getSource()      { return source; }
    public String getEnvironment() { return environment; }
    public String getStatus()      { return status; }
    public String getCode()        { return code; }
    public String getMessage()     { return message; }
    public String getTimestamp()   { return timestamp; }
}
