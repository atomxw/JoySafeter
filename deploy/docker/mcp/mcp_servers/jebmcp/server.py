import os
import sys
import json
import argparse
import http.client
import time

from fastmcp import FastMCP

# The log_level is necessary for Cline to work: https://github.com/jlowin/fastmcp/issues/81
mcp = FastMCP("github.com/flankerhqd/jeb-pro-mcp", log_level="ERROR", host="0.0.0.0", port= int(os.environ.get('JEB_MCP_PORT', 8008)))

jsonrpc_request_id = 1

def make_jsonrpc_request(method: str, *params):
    """Make a JSON-RPC request to the JEB plugin"""
    global jsonrpc_request_id

    # 打印请求日志
    print(f"[JEB MCP] Calling method: {method}, params: {params}", flush=True)

    max_retries = 3
    for attempt in range(max_retries):
        conn = http.client.HTTPConnection(os.environ.get('JEB_SERVER_IP', "localhost"), int(os.environ.get('JEB_SERVER_PORT', 16161)))
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": list(params),
            "id": jsonrpc_request_id,
        }
        jsonrpc_request_id += 1

        try:
            conn.request("POST", "/mcp", json.dumps(request), {
                "Content-Type": "application/json"
            })
            response = conn.getresponse()
            data = json.loads(response.read().decode())

            if "error" in data:
                error = data["error"]
                code = error["code"]
                message = error["message"]
                pretty = f"JSON-RPC error {code}: {message}"
                if "data" in error:
                    pretty += "\n" + error["data"]
                raise Exception(pretty)

            result = data["result"]
            # NOTE: LLMs do not respond well to empty responses
            if result is None:
                result = "empty"
            return result
        except http.client.RemoteDisconnected:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                raise
        except Exception:
            raise
        finally:
            conn.close()

@mcp.tool()
def check_connection() -> str:
    """Check if the JEB plugin is running"""
    try:
        metadata = make_jsonrpc_request("ping")
        return "Successfully connected to JEB Pro"
    except Exception:
        if sys.platform == "darwin":
            shortcut = "Ctrl+Option+M"
        else:
            shortcut = "Ctrl+Alt+M"
        return f"Failed to connect to JEB Pro! Did you run Edit -> Scripts -> MCP ({shortcut}) to start the server?"



SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
JEB_PLUGIN_PY = os.path.join(SCRIPT_DIR, "MCP.py")
GENERATED_PY = os.path.join(SCRIPT_DIR, "server_generated.py")

def generate():
    with open(GENERATED_PY, "r") as f:
        code = f.read()
        exec(compile(code, GENERATED_PY, "exec"))

generate()
def main():
    argparse.ArgumentParser(description="JEB Pro MCP Server")
    #mcp.run(transport="stdio")
    mcp.run(transport="sse")

if __name__ == "__main__":
    main()
