import json
from prance import ResolvingParser

def extract_fields(schema, visited_refs=None):
    if visited_refs is None:
        visited_refs = set()
    if id(schema) in visited_refs:
        return "<circular_reference>"
    visited_refs.add(id(schema))

    if 'allOf' in schema:
        combined = {}
        for subschema in schema['allOf']:
            combined.update(extract_fields(subschema, visited_refs))
        return combined
    elif 'oneOf' in schema or 'anyOf' in schema:
        # For simplicity, take the first option
        key = 'oneOf' if 'oneOf' in schema else 'anyOf'
        return extract_fields(schema[key][0], visited_refs)
    elif 'properties' in schema:
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        fields = {}
        for prop_name, prop_schema in properties.items():
            field_value = extract_fields(prop_schema, visited_refs)
            if prop_name in required:
                fields[prop_name] = field_value
            else:
                fields[prop_name] = field_value  # You can mark optional fields if needed
        return fields
    elif 'type' in schema:
        if schema['type'] == 'array':
            items = extract_fields(schema.get('items', {}), visited_refs)
            return [items]
        elif schema['type'] == 'object':
            return extract_fields(schema.get('properties', {}), visited_refs)
        else:
            if 'default' in schema:
                return schema['default']
            else:
                return "<value>"
    else:
        if 'default' in schema:
            return schema['default']
        else:
            return "<value>"

def construct_json_body(schema):
    return extract_fields(schema)

def generate_curl_commands(spec_string, api_url, default_headers, query_params):
    parser = ResolvingParser(spec_string=spec_string)
    spec = parser.specification
    curl_commands = []

    for path, path_item in spec.get('paths', {}).items():
        for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
            if method in path_item:
                details = path_item[method]
                # Skip deprecated endpoints
                if details.get('deprecated', False):
                    continue
                # Handle path parameters
                full_path = path
                path_params = []
                combined_parameters = path_item.get('parameters', []) + details.get('parameters', [])
                for param in combined_parameters:
                    if param['in'] == 'path':
                        param_name = param['name']
                        full_path = full_path.replace('{' + param_name + '}', f'<{param_name}>')
                # Handle query parameters
                for param in combined_parameters:
                    if param['in'] == 'query':
                        param_name = param['name']
                        query_params.append(f'{param_name}=<{param_name}>')
                query_string = '&'.join(query_params)
                if query_string:
                    full_path += f'?{query_string}'
                # Handle security requirements
                headers = default_headers
                security = details.get('security', spec.get('security', []))
                if security:
                    for sec_requirement in security:
                        for sec_name in sec_requirement:
                            sec_scheme = spec['components']['securitySchemes'][sec_name]
                            if sec_scheme['type'] == 'apiKey':
                                sec_scheme_name = sec_scheme["name"]
                                if sec_scheme['in'] == 'header':
                                    headers.append(f'-H "{sec_scheme_name}: <API_KEY>"')
                                elif sec_scheme['in'] == 'query':
                                    if query_string:
                                        query_string += f'&{sec_scheme_name}=<API_KEY>'
                                    else:
                                        query_string = f'{sec_scheme_name}=<API_KEY>'
                                        full_path += f'?{query_string}'
                            elif sec_scheme['type'] == 'http' and sec_scheme.get('scheme') == 'bearer':
                                headers.append('-H "Authorization: Bearer <token>"')
                # Start building the cURL command
                command = f"curl -X {method.upper()} '{api_url}{full_path}'"
                if headers:
                    command += ' \\\n' + ' \\\n'.join(headers)
                # Handle request body
                if 'requestBody' in details:
                    content = details['requestBody']['content']
                    for content_type, media_type in content.items():
                        schema = media_type['schema']
                        body = construct_json_body(schema)
                        if content_type == 'application/json':
                            json_data = json.dumps(body, indent=4)
                            cmd = command + ' \\\n'
                            cmd += f'-H "Content-Type: {content_type}"' + ' \\\n'
                            cmd += f"-d '{json_data}'"
                        elif content_type == 'multipart/form-data':
                            form_fields = []
                            for key, value in body.items():
                                if isinstance(value, list):
                                    # Handle arrays in form data
                                    for item in value:
                                        if isinstance(item, str) and item == '<value>':
                                            form_fields.append(f'-F "{key}=<value>"')
                                        elif isinstance(item, str) and item == '<file>':
                                            form_fields.append(f'-F "{key}=@/path/to/file"')
                                elif isinstance(value, dict):
                                    # Nested objects in form data (rare in multipart)
                                    pass  # Complex handling needed
                                elif value == '<file>':
                                    form_fields.append(f'-F "{key}=@/path/to/file"')
                                elif value == '<value>':
                                    form_fields.append(f'-F "{key}=<value>"')
                                else:
                                    # Use the actual value, including defaults
                                    form_fields.append(f'-F "{key}={value}"')
                            cmd = command + ' \\\n'
                            cmd += ' \\\n'.join(form_fields)
                        else:
                            # You can add support for other content types here
                            continue  # Unsupported content type
                        curl_commands.append(cmd)
                else:
                    curl_commands.append(command)
    return curl_commands
