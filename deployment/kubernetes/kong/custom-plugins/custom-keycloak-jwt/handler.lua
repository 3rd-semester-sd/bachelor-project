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

local function make_post_request(url, headers, body)
    local httpc = http.new()
    local res, err = httpc:request_uri(
        url,
        {
            method = "POST",
            headers = headers,
            body = body,
        }
    )
    httpc:close()
    return res, err
end

function Plugin:access(config)
    local access_token = ngx.var.http_authorization
    if not access_token then
        return send_json_error(
            ngx.HTTP_UNAUTHORIZED,
            "Access token not found in request headers"
        )
    end

    access_token = access_token:match("Bearer%s+(.+)") or access_token

    local body = ngx.encode_args({
        token = access_token,
        client_id = config.client_id,
        client_secret = config.client_secret,
    })

    local headers = {
        ["Content-Type"] = "application/x-www-form-urlencoded",
    }

    local introspection_url = config.keycloak_introspection_url

    ngx.log(
        ngx.NOTICE,
        "Token introspection request: ",
        cjson.encode({
            url = introspection_url,
            headers = headers,
            body = body,
        })
    )

    local res, err = make_post_request(introspection_url, headers, body)
    if not res then
        return send_json_error(
            ngx.HTTP_INTERNAL_SERVER_ERROR,
            "Failed to introspect token: " .. err
        )
    end

    ngx.log(ngx.NOTICE, "Token introspection response: ", res.body)
    if res.status ~= 200 then
        return send_json_error(
            ngx.HTTP_UNAUTHORIZED,
            "Token introspection failed with status: " .. res.status
        )
    end

    local introspection_result = cjson.decode(res.body)
    if not introspection_result.active then
        return send_json_error(
            ngx.HTTP_UNAUTHORIZED,
            "Access token is not active"
        )
    end

    ngx.req.set_header("X-User-Id", introspection_result.sub)
end

return Plugin
