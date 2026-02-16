classdef MetaValidator
% METAVALIDATOR Validates schema files against the meta-schema.
%   Uses standard JSON Schema Draft 7 meta-schema (did_schema_meta.json)
%   to validate that schema files are well-formed.
%
% TODO: Full JSON Schema Draft 7 compliance is deferred. Current
% implementation checks required keys and basic types only. When
% jsonschema.Validator (MATLAB R2022b+) is available, it will be used
% for full compliance.
%
%   See also: did.schema.Schema, did.schema.Validator, did.schema.ValidationResult

    methods (Static)

        function result = validate(schema_path_or_struct)
            % VALIDATE Validate a schema file against did_schema_meta.json.
            %   result = did.schema.MetaValidator.validate(schema_path_or_struct)
            %   Returns a did.schema.ValidationResult.

            result = did.schema.ValidationResult();

            % Load the schema to validate
            if ischar(schema_path_or_struct) || isstring(schema_path_or_struct)
                try
                    schema_data = did.schema.util.loadJSON(schema_path_or_struct);
                catch me
                    result = result.add_error(sprintf( ...
                        'Could not load schema file: %s', me.message));
                    return;
                end
            elseif isstruct(schema_path_or_struct)
                schema_data = schema_path_or_struct;
            else
                result = result.add_error('Input must be a file path or struct.');
                return;
            end

            % Try to use MATLAB's built-in jsonschema.Validator if available
            % TODO: Full JSON Schema Draft 7 compliance via jsonschema.Validator.
            % For now, use lightweight structural checking.

            % Perform structural validation
            result = did.schema.MetaValidator.validate_structure(schema_data, result);
        end

        function p = meta_schema_path()
            % META_SCHEMA_PATH Return the filesystem path to did_schema_meta.json.
            %   p = did.schema.MetaValidator.meta_schema_path()
            %   Resolves relative to the location of this .m file.

            this_file = mfilename('fullpath');
            this_dir = fileparts(this_file);
            % Navigate from +did/+schema/ to repo root, then into schemas/meta/
            repo_root = fileparts(fileparts(fileparts(this_dir)));
            p = fullfile(repo_root, 'schemas', 'meta', 'did_schema_meta.json');
        end

    end

    methods (Static, Access = private)

        function result = validate_structure(schema_data, result)
            % VALIDATE_STRUCTURE Lightweight structural validation of schema data.
            %   Checks required keys, types, and patterns without full JSON
            %   Schema Draft 7 compliance.

            % Valid type strings
            valid_types = {'did_uid', 'char', 'string', 'integer', 'double', ...
                           'matrix', 'timestamp', 'boolean', 'structure'};

            % Check that it is a struct
            if ~isstruct(schema_data)
                result = result.add_error('Schema must be a JSON object (struct).');
                return;
            end

            % Check required top-level keys
            required_keys = {'classname', 'class_version', 'superclasses', ...
                             'depends_on', 'file', 'fields'};
            for i = 1:numel(required_keys)
                if ~isfield(schema_data, required_keys{i})
                    result = result.add_error(sprintf( ...
                        'Missing required top-level key: "%s".', required_keys{i}));
                end
            end

            if ~result.is_valid
                return; % Missing keys, can't continue
            end

            % Check for unrecognized top-level keys
            actual_keys = fieldnames(schema_data);
            for i = 1:numel(actual_keys)
                if ~ismember(actual_keys{i}, required_keys)
                    result = result.add_error(sprintf( ...
                        'Unrecognized top-level key: "%s".', actual_keys{i}));
                end
            end

            % Validate classname
            cn = schema_data.classname;
            if ~ischar(cn) && ~isstring(cn)
                result = result.add_error('classname must be a string.');
            elseif isempty(regexp(char(cn), '^[a-zA-Z][a-zA-Z0-9_]*$', 'once'))
                result = result.add_error(sprintf( ...
                    'classname "%s" does not match required pattern ^[a-zA-Z][a-zA-Z0-9_]*$.', ...
                    char(cn)));
            end

            % Validate class_version
            cv = schema_data.class_version;
            if ~ischar(cv) && ~isstring(cv)
                result = result.add_error('class_version must be a string.');
            elseif isempty(regexp(char(cv), '^\d+\.\d+\.\d+$', 'once'))
                result = result.add_error(sprintf( ...
                    'class_version "%s" does not match MAJOR.MINOR.PATCH format.', ...
                    char(cv)));
            end

            % Validate superclasses array
            supers = schema_data.superclasses;
            if ~isempty(supers)
                if isstruct(supers)
                    supers_list = num2cell(supers);
                elseif iscell(supers)
                    supers_list = supers;
                else
                    result = result.add_error('superclasses must be an array.');
                    supers_list = {};
                end
                for i = 1:numel(supers_list)
                    s = supers_list{i};
                    if ~isstruct(s)
                        result = result.add_error(sprintf( ...
                            'superclasses[%d] must be an object.', i));
                        continue;
                    end
                    if ~isfield(s, 'classname') || ~(ischar(s.classname) || isstring(s.classname))
                        result = result.add_error(sprintf( ...
                            'superclasses[%d] must have a string "classname" key.', i));
                    end
                    if ~isfield(s, 'schema') || ~(ischar(s.schema) || isstring(s.schema))
                        result = result.add_error(sprintf( ...
                            'superclasses[%d] must have a string "schema" key.', i));
                    end
                end
            end

            % Validate depends_on array
            deps = schema_data.depends_on;
            if ~isempty(deps)
                if isstruct(deps)
                    deps_list = num2cell(deps);
                elseif iscell(deps)
                    deps_list = deps;
                else
                    result = result.add_error('depends_on must be an array.');
                    deps_list = {};
                end
                for i = 1:numel(deps_list)
                    d = deps_list{i};
                    if ~isstruct(d)
                        result = result.add_error(sprintf( ...
                            'depends_on[%d] must be an object.', i));
                        continue;
                    end
                    if ~isfield(d, 'name') || ~(ischar(d.name) || isstring(d.name))
                        result = result.add_error(sprintf( ...
                            'depends_on[%d] must have a string "name" key.', i));
                    end
                    if ~isfield(d, 'mustBeNonEmpty') || ~islogical(d.mustBeNonEmpty)
                        % jsondecode may produce 0/1 instead of logical
                        if isfield(d, 'mustBeNonEmpty') && isnumeric(d.mustBeNonEmpty) && ...
                                (d.mustBeNonEmpty == 0 || d.mustBeNonEmpty == 1)
                            % acceptable numeric boolean
                        else
                            result = result.add_error(sprintf( ...
                                'depends_on[%d].mustBeNonEmpty must be a boolean.', i));
                        end
                    end
                    if ~isfield(d, 'documentation') || ~(ischar(d.documentation) || isstring(d.documentation))
                        result = result.add_error(sprintf( ...
                            'depends_on[%d] must have a string "documentation" key.', i));
                    end
                end
            end

            % Validate file array
            files = schema_data.file;
            if ~isempty(files)
                if isstruct(files)
                    files_list = num2cell(files);
                elseif iscell(files)
                    files_list = files;
                else
                    result = result.add_error('file must be an array.');
                    files_list = {};
                end
                for i = 1:numel(files_list)
                    f = files_list{i};
                    if ~isstruct(f)
                        result = result.add_error(sprintf( ...
                            'file[%d] must be an object.', i));
                        continue;
                    end
                    if ~isfield(f, 'name') || ~(ischar(f.name) || isstring(f.name))
                        result = result.add_error(sprintf( ...
                            'file[%d] must have a string "name" key.', i));
                    end
                    if ~isfield(f, 'documentation') || ~(ischar(f.documentation) || isstring(f.documentation))
                        result = result.add_error(sprintf( ...
                            'file[%d] must have a string "documentation" key.', i));
                    end
                end
            end

            % Validate fields array
            fields = schema_data.fields;
            if ~isempty(fields)
                if isstruct(fields)
                    fields_list = num2cell(fields);
                elseif iscell(fields)
                    fields_list = fields;
                else
                    result = result.add_error('fields must be an array.');
                    fields_list = {};
                end
                for i = 1:numel(fields_list)
                    if iscell(fields_list)
                        fld = fields_list{i};
                    else
                        fld = fields_list(i);
                    end
                    result = did.schema.MetaValidator.validate_field_definition( ...
                        fld, sprintf('fields[%d]', i), valid_types, result);
                end
            end
        end

        function result = validate_field_definition(field_def, path, valid_types, result)
            % VALIDATE_FIELD_DEFINITION Validate a single field definition object.

            if ~isstruct(field_def)
                result = result.add_error(sprintf( ...
                    '%s must be an object.', path));
                return;
            end

            % Required keys for all fields
            required_field_keys = {'name', 'type', 'blank_value', 'default_value', ...
                'mustBeNonEmpty', 'mustBeScalar', 'mustNotHaveNaN', ...
                'queryable', 'ontology', 'documentation', 'constraints'};

            for i = 1:numel(required_field_keys)
                if ~isfield(field_def, required_field_keys{i})
                    result = result.add_error(sprintf( ...
                        '%s is missing required key "%s".', path, required_field_keys{i}));
                end
            end

            % Validate name
            if isfield(field_def, 'name')
                if ~ischar(field_def.name) && ~isstring(field_def.name)
                    result = result.add_error(sprintf('%s.name must be a string.', path));
                elseif isempty(regexp(char(field_def.name), '^[a-zA-Z][a-zA-Z0-9_]*$', 'once'))
                    result = result.add_error(sprintf( ...
                        '%s.name "%s" does not match required pattern.', path, char(field_def.name)));
                end
            end

            % Validate type
            if isfield(field_def, 'type')
                if ~ischar(field_def.type) && ~isstring(field_def.type)
                    result = result.add_error(sprintf('%s.type must be a string.', path));
                elseif ~ismember(char(field_def.type), valid_types)
                    result = result.add_error(sprintf( ...
                        '%s.type "%s" is not a valid type.', path, char(field_def.type)));
                end
            end

            % Validate boolean flags
            bool_keys = {'mustBeNonEmpty', 'mustBeScalar', 'mustNotHaveNaN', 'queryable'};
            for i = 1:numel(bool_keys)
                key = bool_keys{i};
                if isfield(field_def, key)
                    val = field_def.(key);
                    if ~islogical(val)
                        if isnumeric(val) && (val == 0 || val == 1)
                            % acceptable numeric boolean from jsondecode
                        else
                            result = result.add_error(sprintf( ...
                                '%s.%s must be a boolean.', path, key));
                        end
                    end
                end
            end

            % Validate ontology (null or object with namespace, term, uri)
            if isfield(field_def, 'ontology')
                ont = field_def.ontology;
                if ~isempty(ont) % null becomes [] in MATLAB
                    if ~isstruct(ont)
                        result = result.add_error(sprintf( ...
                            '%s.ontology must be null or an object with namespace, term, uri.', path));
                    else
                        ont_keys = {'namespace', 'term', 'uri'};
                        for i = 1:numel(ont_keys)
                            if ~isfield(ont, ont_keys{i})
                                result = result.add_error(sprintf( ...
                                    '%s.ontology is missing required key "%s".', path, ont_keys{i}));
                            end
                        end
                    end
                end
            end

            % Validate documentation
            if isfield(field_def, 'documentation')
                if ~ischar(field_def.documentation) && ~isstring(field_def.documentation)
                    result = result.add_error(sprintf( ...
                        '%s.documentation must be a string.', path));
                end
            end

            % Validate constraints
            if isfield(field_def, 'constraints')
                if ~isstruct(field_def.constraints)
                    % An empty JSON object {} becomes struct() in MATLAB, which is fine.
                    % But if it becomes something else, that's an error.
                    if ~isempty(field_def.constraints)
                        result = result.add_error(sprintf( ...
                            '%s.constraints must be an object.', path));
                    end
                end
            end

            % For structure type, fields key is required
            if isfield(field_def, 'type') && (ischar(field_def.type) || isstring(field_def.type))
                if strcmp(char(field_def.type), 'structure')
                    if ~isfield(field_def, 'fields')
                        result = result.add_error(sprintf( ...
                            '%s has type "structure" but is missing "fields" key.', path));
                    else
                        % Recursively validate nested fields
                        nested = field_def.fields;
                        if ~isempty(nested)
                            if isstruct(nested)
                                nested_list = num2cell(nested);
                            elseif iscell(nested)
                                nested_list = nested;
                            else
                                result = result.add_error(sprintf( ...
                                    '%s.fields must be an array.', path));
                                nested_list = {};
                            end
                            for j = 1:numel(nested_list)
                                result = did.schema.MetaValidator.validate_field_definition( ...
                                    nested_list{j}, sprintf('%s.fields[%d]', path, j), ...
                                    valid_types, result);
                            end
                        end
                    end
                end
            end
        end

    end

end
