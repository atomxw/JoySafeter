# -*- coding: utf-8 -*-

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core.util import DecompilerHelper

from com.pnfsoftware.jeb.core import Artifact, RuntimeProjectUtil

from com.pnfsoftware.jeb.core.input import FileInput
from com.pnfsoftware.jeb.core.units.code.android import IApkUnit
from com.pnfsoftware.jeb.core.output.text import TextDocumentUtil
from com.pnfsoftware.jeb.core.actions import ActionXrefsData, Actions, ActionContext, ActionOverridesData
from java.io import File

import json
import threading
import traceback
import os
import time

# Python 2.7 changes - use urlparse from urlparse module instead of urllib.parse
from urlparse import urlparse
# Python 2.7 doesn't have typing, so we'll define our own minimal substitutes
# and ignore most type annotations

# Mock typing classes/functions for type annotation compatibility
class Any(object): pass
class Callable(object): pass
def get_type_hints(func):
    """Mock for get_type_hints that works with Python 2.7 functions"""
    hints = {}
    
    # Try to get annotations (modern Python way)
    if hasattr(func, '__annotations__'):
        hints.update(getattr(func, '__annotations__', {}))
    
    # For Python 2.7, inspect the function signature
    import inspect
    args, varargs, keywords, defaults = inspect.getargspec(func)
    
    # Add all positional parameters with Any type
    for arg in args:
        if arg not in hints:
            hints[arg] = Any
            
    return hints
class TypedDict(dict): pass
class Optional(object): pass
class Annotated(object): pass
class TypeVar(object): pass
class Generic(object): pass

# Use BaseHTTPServer instead of http.server
import BaseHTTPServer

class JSONRPCError(Exception):
    def __init__(self, code, message, data=None):
        Exception.__init__(self, message)
        self.code = code
        self.message = message
        self.data = data

class RPCRegistry(object):
    def __init__(self):
        self.methods = {}

    def register(self, func):
        self.methods[func.__name__] = func
        return func

    def dispatch(self, method, params):
        if method not in self.methods:
            raise JSONRPCError(-32601, "Method '{0}' not found".format(method))

        func = self.methods[method]
        hints = get_type_hints(func)

        # Remove return annotation if present
        if 'return' in hints:
            hints.pop("return", None)

        if isinstance(params, list):
            if len(params) != len(hints):
                raise JSONRPCError(-32602, "Invalid params: expected {0} arguments, got {1}".format(len(hints), len(params)))

            # Python 2.7 doesn't support zip with items() directly
            # Convert to simpler validation approach
            converted_params = []
            param_items = hints.items()
            for i, value in enumerate(params):
                if i < len(param_items):
                    param_name, expected_type = param_items[i]
                    # In Python 2.7, we'll do minimal type checking
                    converted_params.append(value)
                else:
                    converted_params.append(value)

            return func(*converted_params)
        elif isinstance(params, dict):
            # Simplify type validation for Python 2.7
            if set(params.keys()) != set(hints.keys()):
                raise JSONRPCError(-32602, "Invalid params: expected {0}".format(list(hints.keys())))

            # Validate and convert parameters
            converted_params = {}
            for param_name, expected_type in hints.items():
                value = params.get(param_name)
                # Skip detailed type validation in Python 2.7 version
                converted_params[param_name] = value

            return func(**converted_params)
        else:
            raise JSONRPCError(-32600, "Invalid Request: params must be array or object")

rpc_registry = RPCRegistry()

def jsonrpc(func):
    """Decorator to register a function as a JSON-RPC method"""
    global rpc_registry
    return rpc_registry.register(func)

class JSONRPCRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def send_jsonrpc_error(self, code, message, id=None):
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            }
        }
        if id is not None:
            response["id"] = id
        response_body = json.dumps(response)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response_body))
        self.end_headers()
        self.wfile.write(response_body)

    def do_POST(self):
        global rpc_registry

        parsed_path = urlparse(self.path)
        if parsed_path.path != "/mcp":
            self.send_jsonrpc_error(-32098, "Invalid endpoint", None)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self.send_jsonrpc_error(-32700, "Parse error: missing request body", None)
            return

        request_body = self.rfile.read(content_length)
        try:
            request = json.loads(request_body)
        except ValueError:  # Python 2.7 uses ValueError instead of JSONDecodeError
            self.send_jsonrpc_error(-32700, "Parse error: invalid JSON", None)
            return

        # Prepare the response
        response = {
            "jsonrpc": "2.0"
        }
        if request.get("id") is not None:
            response["id"] = request.get("id")

        try:
            # Basic JSON-RPC validation
            if not isinstance(request, dict):
                raise JSONRPCError(-32600, "Invalid Request")
            if request.get("jsonrpc") != "2.0":
                raise JSONRPCError(-32600, "Invalid JSON-RPC version")
            if "method" not in request:
                raise JSONRPCError(-32600, "Method not specified")

            # Dispatch the method
            result = rpc_registry.dispatch(request["method"], request.get("params", []))
            response["result"] = result

        except JSONRPCError as e:
            response["error"] = {
                "code": e.code,
                "message": e.message
            }
            if e.data is not None:
                response["error"]["data"] = e.data
        except Exception:
            traceback.print_exc()
            response["error"] = {
                "code": -32603,
                "message": "Internal error (please report a bug)",
                "data": traceback.format_exc(),
            }

        try:
            response_body = json.dumps(response)
        except Exception:
            traceback.print_exc()
            response_body = json.dumps({
                "error": {
                    "code": -32603,
                    "message": "Internal error (please report a bug)",
                    "data": traceback.format_exc(),
                }
            })

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response_body))
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format, *args):
        # Suppress logging
        pass

class MCPHTTPServer(BaseHTTPServer.HTTPServer):
    allow_reuse_address = False

class Server(object):  # Use explicit inheritance from object for py2
    HOST = "0.0.0.0"
    PORT = int(os.environ.get('JEB_SERVER_PORT', 16161))

    def __init__(self):
        self.server = None
        self.server_thread = None
        self.running = False

    def start(self):
        if self.running:
            print("[MCP] Server is already running")
            return

        # Python 2.7 doesn't support daemon parameter in Thread constructor
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True  # Set daemon attribute after creation
        self.running = True
        self.server_thread.start()

    def stop(self):
        if not self.running:
            return

        self.running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join()
            self.server = None
        print("[MCP] Server stopped")

    def _run_server(self):
        try:
            # Create server in the thread to handle binding
            self.server = MCPHTTPServer((Server.HOST, Server.PORT), JSONRPCRequestHandler)
            print("[MCP] Server started at http://{0}:{1}".format(Server.HOST, Server.PORT))
            self.server.serve_forever()
        except OSError as e:
            if e.errno == 98 or e.errno == 10048:  # Port already in use (Linux/Windows)
                print("[MCP] Error: Port 13337 is already in use")
            else:
                print("[MCP] Server error: {0}".format(e))
            self.running = False
        except Exception as e:
            print("[MCP] Server error: {0}".format(e))
        finally:
            self.running = False

# A module that helps with writing thread safe ida code.
# Based on:
# https://web.archive.org/web/20160305190440/http://www.williballenthin.com/blog/2015/09/04/idapython-synchronization-decorator/

@jsonrpc
def ping():
    """Do a simple ping to check server is alive and running"""
    return "pong"

# implement a FIFO queue to store the artifacts
artifactQueue = list()

def addArtifactToQueue(artifact):
    """Add an artifact to the queue"""
    artifactQueue.append(artifact)

def getArtifactFromQueue():
    """Get an artifact from the queue"""
    if len(artifactQueue) > 0:
        return artifactQueue.pop(0)
    return None

def clearArtifactQueue():
    """Clear the artifact queue"""
    global artifactQueue
    artifactQueue = list()

MAX_OPENED_ARTIFACTS = 1

# 全局缓存，目前只缓存了exported_activities，加载新的apk文件时将被清除。
apk_cached_data = {}

def getOrLoadApk(filepath):
    engctx = CTX.getEnginesContext()

    if not engctx:
        print('Back-end engines not initialized')
        return

    if not os.path.exists(filepath):
        raise Exception("File not found: %s" % filepath)
    # Create a project
    project = engctx.loadProject('MCPPluginProject')
    correspondingArtifact = None
    for artifact in project.getLiveArtifacts():
        if artifact.getArtifact().getName() == filepath:
            # If the artifact is already loaded, return it
            correspondingArtifact = artifact
            break
    if not correspondingArtifact:
        # try to load the artifact, but first check if the queue size has been exceeded
        if len(artifactQueue) >= MAX_OPENED_ARTIFACTS:
            # unload the oldest artifact
            oldestArtifact = getArtifactFromQueue()
            if oldestArtifact:
                # unload the artifact
                oldestArtifactName = oldestArtifact.getArtifact().getName()
                print('Unloading artifact: %s because queue size limit exeeded' % oldestArtifactName)
                RuntimeProjectUtil.destroyLiveArtifact(oldestArtifact)

        # Fix: 直接用filepath而不是basename作为Artifact的名称，否则如果加载了多个同名不同路径的apk，会出现问题。
        correspondingArtifact = project.processArtifact(Artifact(filepath, FileInput(File(filepath))))
        addArtifactToQueue(correspondingArtifact)
        apk_cached_data.clear()
    
    unit = correspondingArtifact.getMainUnit()
    if isinstance(unit, IApkUnit):
        # If the unit is already loaded, return it
        return unit    
    return None


@jsonrpc
def get_manifest(filepath):
    """Get the manifest of the given APK file in path, note filepath needs to be an absolute path"""
    if not filepath:
        return None

    apk = getOrLoadApk(filepath)  # Fixed: use getOrLoadApk function to load the APK
    #get base name
    
    if apk is None:
        # if the input is not apk (e.g. a jar or single dex)
        # assume it runs in system context
        return None
    
    if 'manifest' in apk_cached_data:
        return apk_cached_data['manifest']
    
    man = apk.getManifest()
    if man is None:
        return None
    doc = man.getFormatter().getPresentation(0).getDocument()
    text = TextDocumentUtil.getText(doc)
    #engctx.unloadProjects(True)
    apk_cached_data['manifest'] = text
    return text


@jsonrpc
def get_all_exported_activities(filepath):
    """
    Get all exported Activity components from the APK and normalize their class names.

    An Activity is considered "exported" if:
    - It explicitly sets android:exported="true", or
    - It omits android:exported but includes an <intent-filter> (implicitly exported)

    Note:
    - If android:exported="false" is explicitly set, the Activity is NOT exported, even if it has intent-filters.

    Class name normalization rules:
    - If it starts with '.', prepend the package name (e.g., .MainActivity -> com.example.app.MainActivity)
    - If it has no '.', include both the original and package-prefixed versions
    - If it’s a full class name, keep as-is

    Returns a list of fully qualified exported Activity class names (for use in decompilation, etc.)
    """
    if not filepath:
        return []
    
    # 首先尝试在缓存中取
    if 'exported_activities' in apk_cached_data:
        return apk_cached_data['exported_activities']
    
    from xml.etree import ElementTree as ET

    manifest_text = get_manifest(filepath)
    manifest_text = manifest_text.replace('&', '&amp;')

    if not manifest_text:
        return []

    try:
        root = ET.fromstring(manifest_text.encode('utf-8'))
    except Exception as e:
        print("[MCP] Error parsing manifest:", e)
        return []

    ANDROID_NS = 'http://schemas.android.com/apk/res/android'
    exported_activities = []

    # 获取包名
    package_name = root.attrib.get('package', '').strip()

    # 查找 <application> 节点
    app_node = root.find('application')
    if app_node is None:
        return []

    for activity in app_node.findall('activity'):
        name = activity.attrib.get('{' + ANDROID_NS + '}name')
        exported = activity.attrib.get('{' + ANDROID_NS + '}exported')
        has_intent_filter = len(activity.findall('intent-filter')) > 0

        if not name:
            continue

        if exported == "true" or (exported is None and has_intent_filter):
            normalized = set()

            if name.startswith('.'):
                normalized.add(package_name + name)
            elif '.' not in name:
                normalized.add(name)
                normalized.add(package_name + '.' + name)
            else:
                normalized.add(name)

            exported_activities.extend(normalized)
    # 缓存导出Activity数据
    apk_cached_data['exported_activities'] = exported_activities
    return exported_activities


@jsonrpc
def get_exported_activities_count(filepath):
    exported_activities = get_all_exported_activities(filepath)
    return len(exported_activities)


@jsonrpc
def get_an_exported_activity_by_index(filepath, index):
    exported_activities = get_all_exported_activities(filepath)
    if index >= 0 and index < len(exported_activities):
        return exported_activities[index]
    else:
        return None


@jsonrpc
def get_method_decompiled_code(filepath, method_signature):
    """Get the decompiled code of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    Dex units use Java-style internal addresses to identify items:
    - package: Lcom/abc/
    - type: Lcom/abc/Foo;
    - method: Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    - field: Lcom/abc/Foo;->flag1:Z
    note filepath needs to be an absolute path
    """
    if not filepath or not method_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None
    
    codeUnit = apk.getDex()
    method = codeUnit.getMethod(method_signature)
    decomp = DecompilerHelper.getDecompiler(codeUnit)
    if not decomp:
        print('Cannot acquire decompiler for unit: %s' % decomp)
        return
    
    if method is None:
        print('[MCP] Method not found: %s' % method_signature)
        return None

    if not decomp.decompileMethod(method.getSignature()):
        print('Failed decompiling method')
        return

    text = decomp.getDecompiledMethodText(method.getSignature())
    return text


@jsonrpc
def get_method_smali_code(filepath, method_signature):
    """Get the smali code of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    Dex units use Java-style internal addresses to identify items:
    - package: Lcom/abc/
    - type: Lcom/abc/Foo;
    - method: Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    - field: Lcom/abc/Foo;->flag1:Z
    note filepath needs to be an absolute path
    """
    if not filepath or not method_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None
    
    codeUnit = apk.getDex()
    method = codeUnit.getMethod(method_signature)

    if method is None:
        print('[MCP] Method not found: %s' % method_signature)
        return None
    
    instructions = method.getInstructions()
    smali_code = ""
    for instruction in instructions:
        smali_code = smali_code + instruction.format(None)  + "\n"

    return smali_code


@jsonrpc
def get_class_decompiled_code(filepath, class_signature):
    """Get the decompiled code of the given class in the APK file, the passed in class_signature needs to be a fully-qualified signature
    Dex units use Java-style internal addresses to identify items:
    - package: Lcom/abc/
    - type: Lcom/abc/Foo;
    - method: Lcom/abc/Foo;->bar(I[JLjava/Lang/String;)V
    - field: Lcom/abc/Foo;->flag1:Z
    note filepath needs to be an absolute path
    """
    if not filepath or not class_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None
    
    codeUnit = apk.getDex()
    clazz = codeUnit.getClass(class_signature)
    if clazz is None:
        print('[MCP] Class not found: %s' % class_signature)
        return None

    decomp = DecompilerHelper.getDecompiler(codeUnit)
    if not decomp:
        print('Cannot acquire decompiler for unit: %s' % codeUnit)
        return None

    if not decomp.decompileClass(clazz.getSignature()):
        print('Failed decompiling class: %s' % class_signature)
        return None

    text = decomp.getDecompiledClassText(clazz.getSignature())
    return text


@jsonrpc
def get_method_callers(filepath, method_signature):
    """
    Get the callers of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    note filepath needs to be an absolute path
    """
    if not filepath or not method_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None
    
    ret = []
    codeUnit = apk.getDex()
    method = codeUnit.getMethod(method_signature)
    if method is None:
        print("Method not found: %s" % method_signature)
        return []
    actionXrefsData = ActionXrefsData()
    actionContext = ActionContext(codeUnit, Actions.QUERY_XREFS, method.getItemId(), None)
    if codeUnit.prepareExecution(actionContext,actionXrefsData):
        for i in range(actionXrefsData.getAddresses().size()):
            ret.append({
                "address": actionXrefsData.getAddresses()[i],
                "details": actionXrefsData.getDetails()[i]
            })
    return ret


@jsonrpc
def get_field_callers(filepath, field_signature):
    """
    Get the callers of the given field in the APK file, the passed in field_signature needs to be a fully-qualified signature
    note filepath needs to be an absolute path
    """
    if not filepath or not field_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None
    
    ret = []
    codeUnit = apk.getDex()
    field = codeUnit.getField(field_signature)
    if field is None:
        print("Field not found: %s" % field_signature)
        return []
    actionXrefsData = ActionXrefsData()
    actionContext = ActionContext(codeUnit, Actions.QUERY_XREFS, field.getItemId(), None)
    if codeUnit.prepareExecution(actionContext,actionXrefsData):
        for i in range(actionXrefsData.getAddresses().size()):
            ret.append({
                "address": actionXrefsData.getAddresses()[i],
                "details": actionXrefsData.getDetails()[i]
            })
    return ret


@jsonrpc
def get_method_overrides(filepath, method_signature):
    """
    Get the overrides of the given method in the APK file, the passed in method_signature needs to be a fully-qualified signature
    note filepath needs to be an absolute path
    """
    if not filepath or not method_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None
    
    ret = []
    codeUnit = apk.getDex()
    method = codeUnit.getMethod(method_signature)
    if method is None:
        print("Method not found: %s" % method_signature)
        return []
    data = ActionOverridesData()
    actionContext = ActionContext(codeUnit, Actions.QUERY_OVERRIDES, method.getItemId(), None)
    if codeUnit.prepareExecution(actionContext,data):
        for i in range(data.getAddresses().size()):
            ret.append(data.getAddresses()[i])
    return ret


@jsonrpc
def get_superclass(filepath, class_signature):
    if not filepath or not class_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None

    codeUnit = apk.getDex()
    clazz = codeUnit.getClass(class_signature)
    if clazz is None:
        return None

    return clazz.getSupertypeSignature(True)


@jsonrpc
def get_interfaces(filepath, class_signature):
    if not filepath or not class_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None

    codeUnit = apk.getDex()
    clazz = codeUnit.getClass(class_signature)
    if clazz is None:
        return None
    
    interfaces = []
    interfaces_array = clazz.getInterfaceSignatures(True)
    for interface in interfaces_array:
        interfaces.append(interface)

    return interfaces


@jsonrpc
def get_class_methods(filepath, class_signature):
    if not filepath or not class_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None

    codeUnit = apk.getDex()
    clazz = codeUnit.getClass(class_signature)
    if clazz is None:
        return None
    
    method_signatures = []
    dex_methods = clazz.getMethods()
    for method in dex_methods:
        if method:
            method_signatures.append(method.getSignature(True))

    return method_signatures


@jsonrpc
def get_class_fields(filepath, class_signature):
    if not filepath or not class_signature:
        return None

    apk = getOrLoadApk(filepath)
    if apk is None:
        return None

    codeUnit = apk.getDex()
    clazz = codeUnit.getClass(class_signature)
    if clazz is None:
        return None
    
    field_signatures = []
    dex_field = clazz.getFields()
    for field in dex_field:
        if field:
            field_signatures.append(field.getSignature(True))

    return field_signatures

@jsonrpc
def unload_projects():
    engctx = CTX.getEnginesContext()
    engctx.unloadProjects(True)
    return "projects unload success"

@jsonrpc
def get_activity_inheritance_chain_with_source(filepath, class_signature, max_depth=5):
    """
    Retrieve the full inheritance chain for a given Android Activity class and the decompiled
    source for each class in the chain.

    Params:
      - filepath: absolute path to the APK file
      - class_signature: JVM internal class signature, e.g. Lcom/example/FooActivity;
      - max_depth: maximum depth to traverse

    Returns:
      { "activity_inheritance_chain": [ { "class_name": str, "super_class_name": str or None, "source_code": str }, ... ] }
    """
    if not filepath or not class_signature:
        return {"activity_inheritance_chain": []}

    apk = getOrLoadApk(filepath)
    if apk is None:
        return {"activity_inheritance_chain": []}

    codeUnit = apk.getDex()
    android_bases = set([
        "Landroid/app/Activity;",
        "Landroidx/activity/ComponentActivity;",
        "Landroidx/fragment/app/FragmentActivity;",
        "Landroidx/appcompat/app/AppCompatActivity;",
        "Landroidx/core/app/ComponentActivity;",
        "Ljava/lang/Object;"
    ])

    chain = []
    current = class_signature
    depth = 0
    decomp = DecompilerHelper.getDecompiler(codeUnit)

    while current and depth < max_depth:
        try:
            clazz = codeUnit.getClass(current)
            source_code = ""
            if clazz and decomp:
                if decomp.decompileClass(clazz.getSignature()):
                    source_code = decomp.getDecompiledClassText(clazz.getSignature())
            parent = None
            if clazz:
                parent = clazz.getSupertypeSignature(True)
            chain.append({
                "class_name": current,
                "super_class_name": parent if parent else None,
                "source_code": source_code
            })
            if not parent or parent in android_bases:
                break
            current = parent
            depth += 1
        except Exception as e:
            chain.append({
                "class_name": current,
                "super_class_name": None,
                "source_code": ""
            })
            break

    return {"activity_inheritance_chain": chain}

@jsonrpc
def get_exported_activities_metadata(filepath):
    """
    Extract exported Activity metadata from the APK manifest.
    Returns a list of dicts:
      {
        "activity_name": str,
        "exported": bool,
        "enabled": str or None,
        "permission": str or None,
        "intent_filters": [ { "actions": [str], "has_default": bool, "has_launcher": bool } ]
      }
    """
    if not filepath:
        return []

    manifest_text = get_manifest(filepath)
    if not manifest_text:
        return []

    try:
        from xml.etree import ElementTree as ET
        # Avoid XML parse errors on '&'
        manifest_text = manifest_text.replace('&', '&')
        root = ET.fromstring(manifest_text.encode('utf-8'))
        ANDROID_NS = 'http://schemas.android.com/apk/res/android'
        exported_activities = []
        app_node = root.find('application')
        if app_node is None:
            return []

        for activity in app_node.findall('activity'):
            name = activity.attrib.get('{' + ANDROID_NS + '}name')
            exported_attr = activity.attrib.get('{' + ANDROID_NS + '}exported')
            enabled = activity.attrib.get('{' + ANDROID_NS + '}enabled')
            permission = activity.attrib.get('{' + ANDROID_NS + '}permission')

            intent_filters = []
            for intent_filter in activity.findall('intent-filter'):
                actions = []
                for a in intent_filter.findall('action'):
                    actions.append(a.attrib.get('{' + ANDROID_NS + '}name'))
                categories = []
                for c in intent_filter.findall('category'):
                    categories.append(c.attrib.get('{' + ANDROID_NS + '}name'))
                has_default = 'android.intent.category.DEFAULT' in categories
                has_launcher = 'android.intent.category.LAUNCHER' in categories
                intent_filters.append({
                    "actions": actions,
                    "has_default": has_default,
                    "has_launcher": has_launcher
                })

            if exported_attr is not None:
                exported_val = (exported_attr == "true")
            else:
                exported_val = (len(intent_filters) > 0)

            if exported_val and name:
                exported_activities.append({
                    "activity_name": name,
                    "exported": exported_val,
                    "enabled": enabled if enabled is not None else None,
                    "permission": permission if permission is not None else None,
                    "intent_filters": intent_filters
                })

        return exported_activities
    except Exception as e:
        print("[MCP] Error parsing manifest:", e)
        return []

# ====================
# Deeplink manifest analysis helpers and JSON-RPC endpoint (Python 2.7 compatible)
# ====================
ANDROID_NS = "http://schemas.android.com/apk/res/android"

def A(attr):
    return "{" + ANDROID_NS + "}" + attr

def to_bool(val):
    if val is None:
        return None
    v = val.strip().lower()
    if v in ("true", "1"):
        return True
    if v in ("false", "0"):
        return False
    return None

def resolve_fqcn(name, base_package):
    if not name:
        return ""
    if name.startswith("."):
        return base_package + name
    if "." in name:
        return name
    return base_package + "." + name

def get_target_sdk(root):
    uses_sdk = root.find("uses-sdk")
    if uses_sdk is not None:
        t = uses_sdk.get(A("targetSdkVersion"))
        if t:
            try:
                return int(t)
            except Exception:
                return None
    return None

def collect_intent_filters(activity_el):
    filters = []
    for if_el in activity_el.findall("intent-filter"):
        actions = []
        categories = []
        data_specs = []
        for child in if_el:
            tag = child.tag
            if tag == "action":
                name = child.get(A("name"))
                if name:
                    actions.append(name)
            elif tag == "category":
                name = child.get(A("name"))
                if name:
                    categories.append(name)
            elif tag == "data":
                data_specs.append({
                    "scheme": child.get(A("scheme")),
                    "host": child.get(A("host")),
                    "port": child.get(A("port")),
                    "path": child.get(A("path")),
                    "pathPrefix": child.get(A("pathPrefix")),
                    "pathPattern": child.get(A("pathPattern")),
                    "mimeType": child.get(A("mimeType")),
                })
        filters.append({
            "actions": actions,
            "categories": categories,
            "data": data_specs
        })
    return filters

def aggregate_deeplink_config(intent_filters):
    schemes = set()
    hosts = set()
    path_patterns = []
    actions = set()
    categories = set()

    for f in intent_filters:
        for a in f.get("actions", []):
            actions.add(a)
        for c in f.get("categories", []):
            categories.add(c)
        for d in f.get("data", []):
            s = d.get("scheme")
            h = d.get("host")
            p = d.get("path")
            pp = d.get("pathPrefix")
            ppat = d.get("pathPattern")
            if s:
                schemes.add(s)
            if h:
                hosts.add(h)
            if p:
                path_patterns.append(p)
            if pp:
                path_patterns.append(pp + "/*")
            if ppat:
                path_patterns.append(ppat)
    return schemes, hosts, path_patterns, actions, categories

def assess_wildcards(hosts, path_patterns, schemes):
    HTTP_SCHEMES = set(["http", "https"])
    wildcard_host = False
    for h in hosts:
        if "*" in h:
            wildcard_host = True
            break
    if not hosts and (len(HTTP_SCHEMES.intersection(schemes)) > 0):
        wildcard_host = True
    wildcard_path = False
    for p in path_patterns:
        if ("*" in p) or (".*" in p):
            wildcard_path = True
            break
    return wildcard_host, wildcard_path

def compute_export_and_reachability(explicit_exported, has_intent_filters, target_sdk, categories):
    res = {}
    explanation = []
    warnings = []

    if explicit_exported is None:
        if has_intent_filters and (target_sdk is None or target_sdk < 31):
            exported = True
            implicit_export_risk = True
            explanation.append("Intent-filter present without android:exported on targetSdk<31 → implicitly exported (risk).")
        else:
            exported = False
            implicit_export_risk = False
            if has_intent_filters and (target_sdk is not None and target_sdk >= 31):
                explanation.append("Android 12+: intent-filter present but android:exported missing → installation/build-time error; treat as blocked but needs fix.")
                warnings.append("android:exported missing with intent-filter on targetSdk>=31")
            else:
                explanation.append("No android:exported and no intent-filters → default internal (not exported).")
    else:
        exported = explicit_exported
        implicit_export_risk = False
        explanation.append("Explicit android:exported=\"%s\"." % (str(explicit_exported).lower()))

    is_browsable = ("android.intent.category.BROWSABLE" in categories)

    externally_reachable = False
    if exported is True:
        externally_reachable = True
        explanation.append("Component is explicitly exported → externally reachable.")
    elif has_intent_filters and explicit_exported is None and (target_sdk is None or target_sdk < 31):
        externally_reachable = True
        explanation.append("Implicitly exported via intent-filter on targetSdk<31 → externally reachable.")

    browser_reachable = externally_reachable and is_browsable

    if browser_reachable:
        reachability_level = "BROWSER"
    elif externally_reachable:
        reachability_level = "EXTERNAL"
    else:
        reachability_level = "INTRA_APP"

    res.update({
        "exported": exported,
        "export_type": ("EXPLICIT" if explicit_exported is not None else "IMPLICIT"),
        "implicit_export_risk": implicit_export_risk,
        "is_browsable": is_browsable,
        "externally_reachable": externally_reachable,
        "browser_reachable": browser_reachable,
        "reachability_level": reachability_level,
        "explanation": " ".join(explanation),
        "warnings": warnings
    })
    return res

def analyze_activity_manifest(root, base_package, activity_el, target_sdk):
    name = activity_el.get(A("name"))
    component_type = "activity" if activity_el.tag == "activity" else ("activity-alias" if activity_el.tag == "activity-alias" else activity_el.tag)
    fqcn = resolve_fqcn(name, base_package)
    target_activity_name = activity_el.get(A("targetActivity")) if component_type == "activity-alias" else None
    target_activity_fqcn = resolve_fqcn(target_activity_name, base_package) if target_activity_name else None

    explicit_exported = to_bool(activity_el.get(A("exported")))
    intent_filters = collect_intent_filters(activity_el)
    has_intent_filters = (len(intent_filters) > 0)

    schemes, hosts, path_patterns, actions, categories = aggregate_deeplink_config(intent_filters)
    wildcard_host, wildcard_path = assess_wildcards(hosts, path_patterns, schemes)

    RESERVED_SCHEMES = set(["http", "https", "android-app", "intent"])
    custom_schemes = set([s for s in schemes if s not in RESERVED_SCHEMES])
    custom_scheme_used = (len(custom_schemes) > 0)
    intent_scheme_used = ("intent" in schemes)

    permission = activity_el.get(A("permission"))
    enabled = to_bool(activity_el.get(A("enabled")))
    has_action_view = ("android.intent.action.VIEW" in actions)
    missing_exported_tgt31 = (has_intent_filters and explicit_exported is None and (target_sdk is not None and target_sdk >= 31))

    reach = compute_export_and_reachability(explicit_exported, has_intent_filters, target_sdk, categories)

    result = {
        "component_name": fqcn,
        "component_type": component_type,
        "target_activity": target_activity_fqcn,
        "target_sdk_version": target_sdk,
        "exported": reach.get("exported"),
        "export_type": reach.get("export_type"),
        "implicit_export_risk": reach.get("implicit_export_risk"),
        "permission": permission,
        "enabled": enabled,
        "intent_filters": intent_filters,
        "deeplink_schemes": sorted(list(schemes)),
        "hosts": sorted(list(hosts)),
        "path_patterns": path_patterns,
        "actions": sorted(list(actions)),
        "categories": sorted(list(categories)),
        "is_browsable": reach.get("is_browsable"),
        "externally_reachable": reach.get("externally_reachable"),
        "browser_reachable": reach.get("browser_reachable"),
        "reachability_level": reach.get("reachability_level"),
        "risk_indicators": {
            "wildcard_host": wildcard_host,
            "wildcard_path": wildcard_path,
            "custom_scheme_used": custom_scheme_used,
            "intent_scheme_used": intent_scheme_used,
            "missing_exported_tgt31": missing_exported_tgt31
        },
        "entrypoint_signals": {
            "has_intent_filter": has_intent_filters,
            "has_action_view": has_action_view,
            "is_browsable": reach.get("is_browsable"),
            "has_data_elements": any([len(f.get("data", [])) > 0 for f in intent_filters]),
            "exported_true": (reach.get("exported") is True)
        },
        "explanation": reach.get("explanation"),
        "warnings": reach.get("warnings"),
    }
    return result

@jsonrpc
def analyze_apk_manifest_via_mcp(filepath, target_component=None):
    """
    Analyze APK's AndroidManifest.xml for deeplink security risks.

    Args:
        filepath (str): Absolute path to the APK file.
        target_component (str|None): Optional Activity FQCN to focus on; if omitted, analyze all activities and aliases.

    Returns:
        dict: {
          "manifest_package": str,
          "target_sdk_version": int|None,
          "components_analyzed": int,
          "results": { component_fqcn: analysis_dict, ... }
        }

    Notes:
        - Runs inside JEB (Python 2.7) close to decompiler and manifest decoder.
        - Keeps XML parsing server-side to minimize client logic and reduce round trips.
    """
    if not filepath:
        raise Exception("Missing filepath")

    manifest_text = get_manifest(filepath)
    if not manifest_text or not manifest_text.strip():
        raise Exception("Empty manifest returned by get_manifest")

    try:
        # Ensure XML-compatible text
        manifest_text = manifest_text.replace('&', '&')
        from xml.etree import ElementTree as ET
        root = ET.fromstring(manifest_text.encode('utf-8'))
    except Exception as e:
        raise Exception("Failed to parse manifest XML: %s" % e)

    base_package = root.get("package") or ""
    target_sdk = get_target_sdk(root)
    app = root.find("application")
    if app is None:
        raise Exception("Invalid manifest: missing <application>")

    activities = []
    for act in app.findall("activity"):
        activities.append(act)
    for alias in app.findall("activity-alias"):
        activities.append(alias)

    results = {}
    matched = False
    if target_component:
        for act in activities:
            info = analyze_activity_manifest(root, base_package, act, target_sdk)
            if info.get("component_name") == target_component:
                results[info.get("component_name")] = info
                matched = True
                break
        if not matched:
            for act in activities:
                info = analyze_activity_manifest(root, base_package, act, target_sdk)
                name = info.get("component_name")
                if name and name.endswith(target_component):
                    results[name] = info
                    matched = True
                    break
            if not matched:
                raise Exception("Target component not found: %s" % target_component)
    else:
        for act in activities:
            info = analyze_activity_manifest(root, base_package, act, target_sdk)
            results[info.get("component_name")] = info

    return {
        "manifest_package": base_package,
        "target_sdk_version": target_sdk,
        "components_analyzed": len(results),
        "results": results
    }

CTX = None
class MCPc(IScript):

    def __init__(self):
        self.server = Server()
        print("[MCP] Plugin loaded")

    def run(self, ctx):
        global CTX  # Fixed: use global keyword to modify global variable
        CTX = ctx
        self.server.start()
        print("[MCP] Plugin running")

        # 保持进程存活（通过无限循环或事件监听）
        try:
            print("=================keep alive")
            while True:
                time.sleep(10)  # 避免CPU满载
        except KeyboardInterrupt:
            print("Exiting...")

    def term(self):
        self.server.stop()
