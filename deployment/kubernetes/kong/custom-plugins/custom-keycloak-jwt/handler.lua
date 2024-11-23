local http = require("resty.http")
local cjson = require("cjson")

local Plugin = {}

Plugin.PRIORITY = 1000
Plugin.VERSION = "1.0.0"

local function log_and_exit(log_level, message, status_code)
    ngx.log(log_level, message)
    return ngx.exit(status_code)
end

local function make_post_request(url, headers, body)
    local httpc = http.new()
    local res, err = httpc:request_uri(url, {
        method = "POST",
        headers = headers,
        body = body,
    })
    httpc:close()
    return res, err
end

function Plugin:access(config)
    local access_token = ngx.var.http_authorization
    if not access_token then
        return log_and_exit(ngx.ERR, "Access token not found in request headers", ngx.HTTP_UNAUTHORIZED)
    end

    local headers = {
        ["Content-Type"] = "application/x-www-form-urlencoded",
        ["Authorization"] = "Basic " .. ngx.encode_base64(config.client_id .. ":" .. config.client_secret),
    }
    local body = "token=" .. access_token

    local introspection_url = config.keycloak_introspection_url
    ngx.log(ngx.DEBUG, "Token introspection request: ", cjson.encode({ url = introspection_url, headers = headers }))

    local res, err = make_post_request(introspection_url, headers, body)
    if not res then
        return log_and_exit(ngx.ERR, "Failed to introspect token: " .. err, ngx.HTTP_INTERNAL_SERVER_ERROR)
    end
    if res.status ~= 200 then
        return log_and_exit(ngx.ERR, "Token introspection failed with status: " .. res.status, ngx.HTTP_UNAUTHORIZED)
    end

    local introspection_result = cjson.decode(res.body)
    if not introspection_result.active then
        return log_and_exit(ngx.ERR, "Access token is not active", ngx.HTTP_UNAUTHORIZED)
    end

    ngx.req.set_header("X-User-Id", introspection_result.sub)
    ngx.req.set_header("X-Username", introspection_result.username or "")
    ngx.log(ngx.INFO, "Token introspection successful for user: ", introspection_result.sub)
end

return Plugin
