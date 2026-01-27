# NOTE: This file has been automatically generated, do not modify!
# Architecture based on https://github.com/mrexodia/ida-pro-mcp (MIT License)
from typing import TypeVar

T = TypeVar("T")

@mcp.tool()
def ping() -> str:
    """Do a simple ping to check server is alive and running"""
    return make_jsonrpc_request('ping')

@mcp.tool()
def get_manifest(filepath: str) -> str:
    """Get the manifest of the given APK file in path, the passed in filepath needs to be a fully-qualified absolute path"""
    return make_jsonrpc_request('get_manifest', filepath)

@mcp.tool()
def get_all_exported_activities(filepath: str) -> list[str]:
    """
    Get all exported activity names from the APK manifest.

    This includes activities with:
    - android:exported="true"
    - or no exported attribute but with at least one <intent-filter>
    
    The passed in filepath needs to be a fully-qualified absolute path.
    """
    return make_jsonrpc_request('get_all_exported_activities', filepath)

@mcp.tool()
def get_exported_activities_count(filepath: str) -> int:
    """
    Get exported activities count from the APK manifest.

    This includes activities with:
    - android:exported="true"
    - or no exported attribute but with at least one <intent-filter>
    
    The passed in filepath needs to be a fully-qualified absolute path.
    """
    return make_jsonrpc_request('get_exported_activities_count', filepath)

@mcp.tool()
def get_an_exported_activity_by_index(filepath: str, index: int) -> str:
    """
    Get an exported activity name by index from the APK manifest.

    This includes activities with:
    - android:exported="true"
    - or no exported attribute but with at least one <intent-filter>
    
    The passed in filepath needs to be a fully-qualified absolute path.
    """
    return make_jsonrpc_request('get_an_exported_activity_by_index', filepath, index)

@mcp.tool()
def get_method_decompiled_code(filepath: str, method_signature: str) -> str:
    """Get the decompiled code of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    Dex units use Java-style internal addresses to identify items:
        
    - package: Lcom/abc/
    - type: Lcom/abc/Foo;
    - method: Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    - field: Lcom/abc/Foo;->flag1:Z

    @param filepath: the path to the APK file
    @param method_signature: the fully-qualified method signature to decompile, e.g. Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_method_decompiled_code', filepath, method_signature)

@mcp.tool()
def get_method_smali_code(filepath: str, method_signature: str) -> str:
    """Get the smali code of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    Dex units use Java-style internal addresses to identify items:
        
    - package: Lcom/abc/
    - type: Lcom/abc/Foo;
    - method: Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    - field: Lcom/abc/Foo;->flag1:Z

    @param filepath: the path to the APK file
    @param method_signature: the fully-qualified method signature to decompile, e.g. Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_method_smali_code', filepath, method_signature)

@mcp.tool()
def get_class_decompiled_code(filepath: str, class_signature: str) -> str:
    """Get the decompiled code of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    Dex units use Java-style internal addresses to identify items:

    - package: Lcom/abc/
    - type: Lcom/abc/Foo;
    - method: Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    - field: Lcom/abc/Foo;->flag1:Z

    @param: filepath: The path to the APK file
    @param: class_signature: The fully-qualified signature of the class to decompile, e.g. Lcom/abc/Foo;
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_class_decompiled_code', filepath, class_signature)

@mcp.tool()
def get_method_callers(filepath: str, method_signature: str) -> list[dict]:
    """
    Get the callers of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_method_callers', filepath, method_signature)

@mcp.tool()
def get_field_callers(filepath: str, field_signature: str) -> list[dict]:
    """
    Get the callers of the given field in the APK file, the passed in field_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_field_callers', filepath, field_signature)

@mcp.tool()
def get_method_overrides(filepath: str, method_signature: str) -> list[str]:
    """
    Get the overrides of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_method_overrides', filepath, method_signature)
    
@mcp.tool()
def get_superclass(filepath: str, class_signature: str) -> str:
    """
    Get the superclass of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_superclass', filepath, class_signature)

@mcp.tool()
def get_interfaces(filepath: str, class_signature: str) -> list[str]:
    """
    Get the interfaces of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_interfaces', filepath, class_signature)

@mcp.tool()
def get_class_methods(filepath: str, class_signature: str) -> list[str]:
    """
    Get the methods of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_class_methods', filepath, class_signature)

@mcp.tool()
def get_class_fields(filepath: str, class_signature: str) -> list[str]:
    """
    Get the fields of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    the passed in filepath needs to be a fully-qualified absolute path
    """
    return make_jsonrpc_request('get_class_fields', filepath, class_signature)

@mcp.tool()
def unload_projects():
    """
     unload all current load apks， for release memory
    """
    return make_jsonrpc_request('unload_projects')

@mcp.tool()
def get_activity_inheritance_chain_with_source(filepath: str, class_signature: str, max_depth: int = 5) -> dict:
    """
    Retrieve the full inheritance chain for an Android Activity class and the decompiled source for each link.

    Args:
        filepath: Absolute path to the APK file.
        class_signature: JVM internal class signature (e.g., Lcom/example/FooActivity;).
        max_depth: Maximum number of superclass hops to follow.

    Returns:
        dict: {
          "activity_inheritance_chain": [
            { "class_name": str, "super_class_name": str | None, "source_code": str }
          ]
        }

    Notes:
        - Runs server-side against JEB to minimize round trips.
        - Stops at Android base classes or when no superclass is found.
    """
    return make_jsonrpc_request('get_activity_inheritance_chain_with_source', filepath, class_signature, max_depth)

@mcp.tool()
def get_exported_activities_metadata(filepath: str) -> list[dict]:
    """
    Extract exported Activity metadata from the APK manifest.

    Args:
        filepath: Absolute path to the APK file.

    Returns:
        list[dict]: Each item has the structure:
          {
            "activity_name": str,
            "exported": bool,
            "enabled": str | None,
            "permission": str | None,
            "intent_filters": [ { "actions": [str], "has_default": bool, "has_launcher": bool } ]
          }

    Notes:
        - Exported=true if android:exported="true" or (missing and intent-filters present).
        - Class names are not normalized here (use get_all_exported_activities if needed).
    """
    return make_jsonrpc_request('get_exported_activities_metadata', filepath)

@mcp.tool()
def analyze_apk_manifest_via_mcp(filepath: str, target_component: str | None = None) -> dict:
    """
    Analyze AndroidManifest.xml for deeplink security risks (server-side in JEB).

    Args:
        filepath: Absolute path to the APK file.
        target_component: Optional Activity FQCN to focus on; if omitted, analyze all activities and aliases.

    Returns:
        dict: {
          "manifest_package": str,
          "target_sdk_version": int | None,
          "components_analyzed": int,
          "results": {
            component_fqcn: {
              "exported": bool,
              "export_type": "EXPLICIT" | "IMPLICIT",
              "implicit_export_risk": bool,
              "permission": str | None,
              "enabled": bool | None,
              "intent_filters": [
                { "actions": [str], "categories": [str], "data": [{"scheme": str|None, "host": str|None, "port": str|None, "path": str|None, "pathPrefix": str|None, "pathPattern": str|None, "mimeType": str|None}] }
              ],
              "deeplink_schemes": [str],
              "hosts": [str],
              "path_patterns": [str],
              "actions": [str],
              "categories": [str],
              "is_browsable": bool,
              "externally_reachable": bool,
              "browser_reachable": bool,
              "reachability_level": "EXTERNAL" | "BROWSER" | "INTRA_APP",
              "risk_indicators": {
                "wildcard_host": bool,
                "wildcard_path": bool,
                "custom_scheme_used": bool,
                "intent_scheme_used": bool,
                "missing_exported_tgt31": bool
              },
              "entrypoint_signals": {
                "has_intent_filter": bool,
                "has_action_view": bool,
                "is_browsable": bool,
                "has_data_elements": bool,
                "exported_true": bool
              },
              "explanation": str,
              "warnings": [str]
            }
          }
        }

    Notes:
        - Parsing and analysis happen inside JEB to reduce RPC round trips.
        - Target component supports exact FQCN and fallback suffix match when exact is missing.
    """
    return make_jsonrpc_request('analyze_apk_manifest_via_mcp', filepath, target_component)
