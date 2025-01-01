local http = require("resty.http")
local cjson = require("cjson")

local Plugin = {}

Plugin.PRIORITY = 1000
Plugin.VERSION = "1.0.0"

local function send_json_error(status_code, message)
    ngx.status = status_code
    ngx.header["Content-Type"] = "application/json"
    local response = {
        error = message,
        status_code = status_code,
    }
    ngx.say(cjson.encode(response))
    ngx.exit(status_code)
end

local function make_get_request(url, headers)
    local httpc = http.new()
    local res, err = httpc:request_uri(
        url,
        {
            method = "GET",
            headers = headers,
        }
    )
    httpc:close()
    return res, err
end

function Plugin:access(config)
    -- skip if the request is not for a protected resource
    if not string.match(ngx.var.request_uri, "/protected") then
        return
    end

    ngx.log(ngx.NOTICE, "Request is for a protected resource", ngx.var.request_uri)


    local access_token = ngx.var.http_authorization
    if not access_token then
        return send_json_error(
            ngx.HTTP_UNAUTHORIZED,
            "Access token not found in request headers"
        )
    end

    access_token = access_token:match("Bearer%s+(.+)") or access_token

    local headers = {
        ["accept"] = "application/json",
        ["Authorization"] = "Bearer " .. access_token,
    }

    local service_url = config.current_user_url

    ngx.log(
        ngx.NOTICE,
        "Token validation request to custom service: ",
        cjson.encode({
            url = service_url,
            headers = headers,
        })
    )

    local res, err = make_get_request(service_url, headers)

    if not res then
        return send_json_error(
            ngx.HTTP_INTERNAL_SERVER_ERROR,
            "Failed to validate token: " .. err
        )
    end

    ngx.log(ngx.NOTICE, "Custom service validation response: ", res.body)
    if res.status ~= 200 then
        return send_json_error(
            ngx.HTTP_UNAUTHORIZED,
            "Token validation failed with status: " .. res.status
        )
    end

    local response_json = cjson.decode(res.body)

    if not response_json.data then
        return send_json_error(
            ngx.HTTP_INTERNAL_SERVER_ERROR,
            "Invalid response from custom service"
        )
    end

    local data = response_json.data

    ngx.req.set_header("X-User-Id", data.id)
    ngx.req.set_header("X-User-Email", data.email)
end

return Plugin
