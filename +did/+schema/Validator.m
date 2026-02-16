classdef Validator
% VALIDATOR Contains all validation logic for DID/NDI documents and fields.
%   All methods are static. This class is stateless.
%
%   See also: did.schema.Schema, did.schema.Document, did.schema.ValidationResult

    methods (Static)

        function result = validate_document(doc_struct, schema)
            % VALIDATE_DOCUMENT Validate a document struct against a Schema object.
            %   result = did.schema.Validator.validate_document(doc_struct, schema)
            %
            %   Validates all fields, including inherited ones from superclasses.
            %   Validates depends_on entries.
            %   Returns a did.schema.ValidationResult.
            %
            % TODO: Dependency existence checks (verifying that depends_on values
            % point to real documents in a database) are not implemented at this
            % layer. This layer only checks that mustBeNonEmpty dependencies have
            % non-empty values. Full existence checking is the responsibility of
            % the database layer.

            result = did.schema.ValidationResult();

            % Check version compatibility
            if isfield(doc_struct, 'document_class') && isfield(doc_struct.document_class, 'class_version')
                doc_version = doc_struct.document_class.class_version;
                if ~did.schema.Validator.is_compatible_version(doc_version, schema.class_version)
                    result = result.add_error(sprintf( ...
                        'Version incompatible: document version "%s" vs schema version "%s" (MAJOR mismatch).', ...
                        doc_version, schema.class_version));
                end
            end

            % Validate depends_on entries
            if ~isempty(schema.depends_on)
                dep_defs = schema.depends_on;
                if isfield(doc_struct, 'depends_on')
                    doc_deps = doc_struct.depends_on;
                    if isstruct(doc_deps)
                        doc_deps = num2cell(doc_deps);
                    elseif ~iscell(doc_deps)
                        doc_deps = {};
                    end
                else
                    doc_deps = {};
                end

                for i = 1:numel(dep_defs)
                    if isstruct(dep_defs) && numel(dep_defs) >= i
                        dep_def = dep_defs(i);
                    elseif iscell(dep_defs)
                        dep_def = dep_defs{i};
                    else
                        continue;
                    end

                    dep_name = dep_def.name;
                    must_be_nonempty = false;
                    if isfield(dep_def, 'mustBeNonEmpty')
                        must_be_nonempty = dep_def.mustBeNonEmpty;
                    end

                    if must_be_nonempty
                        % Find this dependency in the document
                        found = false;
                        dep_value = '';
                        for j = 1:numel(doc_deps)
                            if iscell(doc_deps)
                                dd = doc_deps{j};
                            else
                                dd = doc_deps(j);
                            end
                            if isfield(dd, 'name') && strcmp(dd.name, dep_name)
                                found = true;
                                if isfield(dd, 'value')
                                    dep_value = dd.value;
                                end
                                break;
                            end
                        end

                        if ~found
                            result = result.add_error(sprintf( ...
                                'Required dependency "%s" not found in document.', dep_name));
                        elseif ~did.schema.Validator.check_mustBeNonEmpty(dep_value)
                            result = result.add_error(sprintf( ...
                                'Dependency "%s" must be non-empty.', dep_name));
                        end
                    end
                end
            end

            % Validate all fields (this class + superclasses)
            all_fields = schema.all_fields;
            if isstruct(all_fields)
                field_list = num2cell(all_fields);
            elseif iscell(all_fields)
                field_list = all_fields;
            else
                field_list = {};
            end

            for i = 1:numel(field_list)
                if iscell(field_list)
                    field_def = field_list{i};
                else
                    field_def = field_list(i);
                end

                field_name = field_def.name;

                % Find the value in the document by searching property blocks
                value = did.schema.Validator.find_field_value(doc_struct, field_name, schema);
                found = true;
                if iscell(value) && numel(value) == 1 && ischar(value{1}) && strcmp(value{1}, '___FIELD_NOT_FOUND___')
                    found = false;
                end

                if ~found
                    % Field not found in document - only an error if mustBeNonEmpty
                    if isfield(field_def, 'mustBeNonEmpty') && field_def.mustBeNonEmpty
                        field_result = did.schema.ValidationResult();
                        field_result = field_result.add_error(sprintf( ...
                            'Required field "%s" not found in document.', field_name));
                        field_result.field_path = field_name;
                        result = result.merge(field_result);
                    end
                else
                    field_result = did.schema.Validator.validate_field(value, field_def);
                    if ~isempty(field_result.field_path)
                        field_result.field_path = field_name;
                    end
                    result = result.merge(field_result);
                end
            end

        end

        function result = validate_field(value, field_def)
            % VALIDATE_FIELD Validate a single value against a field definition.
            %   result = did.schema.Validator.validate_field(value, field_def)
            %
            %   Applies type check, constraint check, mustBeNonEmpty,
            %   mustBeScalar, mustNotHaveNaN.

            result = did.schema.ValidationResult();
            result.field_path = field_def.name;

            field_type = field_def.type;
            % Treat 'string' as alias for 'char'
            if strcmp(field_type, 'string')
                field_type = 'char';
            end

            % mustBeNonEmpty check
            if isfield(field_def, 'mustBeNonEmpty') && field_def.mustBeNonEmpty
                if ~did.schema.Validator.check_mustBeNonEmpty(value)
                    result = result.add_error(sprintf( ...
                        'Field "%s" must be non-empty.', field_def.name));
                    return; % If empty and required, skip further checks
                end
            end

            % Skip further checks if value is empty and not required
            if ~did.schema.Validator.check_mustBeNonEmpty(value)
                return;
            end

            % Type check
            if ~did.schema.Validator.check_type(value, field_type)
                result = result.add_error(sprintf( ...
                    'Field "%s" has incorrect type. Expected "%s".', ...
                    field_def.name, field_type));
                return; % Skip further checks if type is wrong
            end

            % mustBeScalar check
            if isfield(field_def, 'mustBeScalar') && field_def.mustBeScalar
                if ~did.schema.Validator.check_mustBeScalar(value)
                    result = result.add_error(sprintf( ...
                        'Field "%s" must be scalar.', field_def.name));
                end
            end

            % mustNotHaveNaN check
            if isfield(field_def, 'mustNotHaveNaN') && field_def.mustNotHaveNaN
                if ~did.schema.Validator.check_mustNotHaveNaN(value)
                    result = result.add_error(sprintf( ...
                        'Field "%s" must not contain NaN values.', field_def.name));
                end
            end

            % Type-specific validation
            if strcmp(field_type, 'timestamp')
                if ischar(value) || isstring(value)
                    if ~did.schema.Validator.check_timestamp(value)
                        result = result.add_error(sprintf( ...
                            'Field "%s" is not a valid ISO 8601 UTC timestamp.', field_def.name));
                    end
                end
            end

            if strcmp(field_type, 'did_uid')
                if ischar(value) || isstring(value)
                    if ~did.schema.Validator.check_did_uid(value)
                        result = result.add_error(sprintf( ...
                            'Field "%s" is not a valid DID UID.', field_def.name));
                    end
                end
            end

            % Constraints check
            if isfield(field_def, 'constraints') && ~isempty(field_def.constraints)
                constraints = field_def.constraints;
                if isstruct(constraints) && ~isempty(fieldnames(constraints))
                    if ~did.schema.Validator.check_constraints(value, field_type, constraints)
                        result = result.add_error(sprintf( ...
                            'Field "%s" violates constraints.', field_def.name));
                    end
                end
            end

            % Recursive validation for structure type
            if strcmp(field_type, 'structure') && isfield(field_def, 'fields')
                nested_fields = field_def.fields;
                if isstruct(nested_fields)
                    nested_list = num2cell(nested_fields);
                elseif iscell(nested_fields)
                    nested_list = nested_fields;
                else
                    nested_list = {};
                end

                for i = 1:numel(nested_list)
                    if iscell(nested_list)
                        nf = nested_list{i};
                    else
                        nf = nested_list(i);
                    end
                    if isstruct(value) && isfield(value, nf.name)
                        sub_result = did.schema.Validator.validate_field(value.(nf.name), nf);
                        sub_result.field_path = [field_def.name '.' nf.name];
                        result = result.merge(sub_result);
                    elseif isfield(nf, 'mustBeNonEmpty') && nf.mustBeNonEmpty
                        result = result.add_error(sprintf( ...
                            'Required nested field "%s.%s" not found.', ...
                            field_def.name, nf.name));
                    end
                end
            end

        end

        function ok = check_type(value, type_string)
            % CHECK_TYPE Check if value conforms to the declared type.
            %   ok = did.schema.Validator.check_type(value, type_string)

            % Treat 'string' as alias for 'char'
            if strcmp(type_string, 'string')
                type_string = 'char';
            end

            switch type_string
                case 'did_uid'
                    ok = ischar(value) || isstring(value);
                case 'char'
                    ok = ischar(value) || isstring(value);
                case 'integer'
                    ok = isnumeric(value) && isreal(value) && all(value == floor(value));
                case 'double'
                    ok = isnumeric(value) && isfloat(value);
                case 'matrix'
                    ok = isnumeric(value);
                case 'timestamp'
                    ok = ischar(value) || isstring(value);
                case 'boolean'
                    ok = islogical(value) || (isnumeric(value) && (value == 0 || value == 1));
                case 'structure'
                    ok = isstruct(value);
                otherwise
                    ok = false;
            end
        end

        function ok = check_constraints(value, type_string, constraints)
            % CHECK_CONSTRAINTS Check if value satisfies type-specific constraints.
            %   ok = did.schema.Validator.check_constraints(value, type_string, constraints)

            ok = true;

            if ~isstruct(constraints) || isempty(fieldnames(constraints))
                return;
            end

            % Treat 'string' as alias for 'char'
            if strcmp(type_string, 'string')
                type_string = 'char';
            end

            switch type_string
                case 'char'
                    if isfield(constraints, 'max_length') && ~isempty(constraints.max_length)
                        if (ischar(value) || isstring(value)) && strlength(string(value)) > constraints.max_length
                            ok = false;
                        end
                    end

                case 'integer'
                    if isfield(constraints, 'min') && ~isempty(constraints.min)
                        if any(value < constraints.min)
                            ok = false;
                        end
                    end
                    if isfield(constraints, 'max') && ~isempty(constraints.max)
                        if any(value > constraints.max)
                            ok = false;
                        end
                    end

                case 'double'
                    if isfield(constraints, 'min') && ~isempty(constraints.min)
                        if any(value < constraints.min)
                            ok = false;
                        end
                    end
                    if isfield(constraints, 'max') && ~isempty(constraints.max)
                        if any(value > constraints.max)
                            ok = false;
                        end
                    end

                case 'matrix'
                    % TODO: Row/column dimension checking requires the value to
                    % actually be a 2D numeric array. The current implementation
                    % tolerates 1D arrays with a warning.
                    if isfield(constraints, 'rows') && ~isempty(constraints.rows)
                        if ismatrix(value) && size(value, 1) ~= constraints.rows
                            ok = false;
                        end
                    end
                    if isfield(constraints, 'cols') && ~isempty(constraints.cols)
                        if ismatrix(value) && size(value, 2) ~= constraints.cols
                            ok = false;
                        end
                    end
                    if isfield(constraints, 'min') && ~isempty(constraints.min)
                        if any(value(:) < constraints.min)
                            ok = false;
                        end
                    end
                    if isfield(constraints, 'max') && ~isempty(constraints.max)
                        if any(value(:) > constraints.max)
                            ok = false;
                        end
                    end
            end
        end

        function ok = check_mustBeNonEmpty(value)
            % CHECK_MUSTBENONEMPTY Check if value is non-empty.
            %   ok = did.schema.Validator.check_mustBeNonEmpty(value)
            %   Returns false if value is [], {}, '', or isempty.

            if isempty(value)
                ok = false;
                return;
            end

            if ischar(value) && strcmp(value, '')
                ok = false;
                return;
            end

            if isstring(value) && strlength(value) == 0
                ok = false;
                return;
            end

            if iscell(value) && isempty(value)
                ok = false;
                return;
            end

            if isstruct(value) && isempty(fieldnames(value))
                ok = false;
                return;
            end

            ok = true;
        end

        function ok = check_mustBeScalar(value)
            % CHECK_MUSTBESCALAR Check if value is scalar.
            %   ok = did.schema.Validator.check_mustBeScalar(value)
            %   Returns false if numel(value) != 1 for numeric/logical,
            %   or if the value is a cell array or non-scalar struct.

            if iscell(value)
                ok = false;
                return;
            end

            if isstruct(value)
                ok = numel(value) == 1;
                return;
            end

            if isnumeric(value) || islogical(value)
                ok = numel(value) == 1;
                return;
            end

            % Strings/chars: a single string is considered scalar
            if isstring(value)
                ok = numel(value) == 1;
                return;
            end

            if ischar(value)
                ok = true; % character vectors are scalar strings
                return;
            end

            ok = true;
        end

        function ok = check_mustNotHaveNaN(value)
            % CHECK_MUSTNOTHAVENAN Check that value contains no NaN.
            %   ok = did.schema.Validator.check_mustNotHaveNaN(value)
            %   Returns false if any element of value is NaN.

            if isnumeric(value)
                ok = ~any(isnan(value(:)));
            else
                ok = true;
            end
        end

        function ok = check_timestamp(value)
            % CHECK_TIMESTAMP Validate ISO 8601 UTC timestamp format.
            %   ok = did.schema.Validator.check_timestamp(value)
            %   Returns true if value is a string matching ISO 8601 UTC format.

            if ~ischar(value) && ~isstring(value)
                ok = false;
                return;
            end

            value = char(value);

            % Match ISO 8601 UTC: YYYY-MM-DDTHH:MM:SS[.sss]Z
            pattern = '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$';
            ok = ~isempty(regexp(value, pattern, 'once'));
        end

        function ok = check_did_uid(value)
            % CHECK_DID_UID Validate a DID unique identifier.
            %   ok = did.schema.Validator.check_did_uid(value)
            %   Returns true if value looks like a valid DID UID.
            %
            % TODO: The exact UID format regex is not yet standardized. For now,
            % accept any non-empty string that is 33+ characters and contains
            % only hex characters and underscores.

            if ~ischar(value) && ~isstring(value)
                ok = false;
                return;
            end

            value = char(value);

            if isempty(value)
                ok = false;
                return;
            end

            % Accept any non-empty string that is 33+ characters and contains
            % only hex characters and underscores
            if length(value) < 33
                ok = false;
                return;
            end

            ok = ~isempty(regexp(value, '^[0-9a-fA-F_]+$', 'once'));
        end

        function [major, minor, patch] = parse_semver(version_string)
            % PARSE_SEMVER Parse a semantic version string.
            %   [major, minor, patch] = did.schema.Validator.parse_semver(version_string)
            %   Throws if malformed.

            [major, minor, patch] = did.schema.util.semver(version_string);
        end

        function ok = is_compatible_version(doc_version, schema_version)
            % IS_COMPATIBLE_VERSION Check if two semver strings are compatible.
            %   ok = did.schema.Validator.is_compatible_version(doc_version, schema_version)
            %   Returns true if doc_version and schema_version have the same
            %   MAJOR component.

            [doc_major, ~, ~] = did.schema.Validator.parse_semver(doc_version);
            [schema_major, ~, ~] = did.schema.Validator.parse_semver(schema_version);

            ok = (doc_major == schema_major);
        end

    end

    methods (Static, Access = private)

        function value = find_field_value(doc_struct, field_name, schema)
            % FIND_FIELD_VALUE Search for a field value in the document struct.
            %   Searches through property blocks (classname-keyed sub-structs).

            sentinel = {'___FIELD_NOT_FOUND___'};

            % Determine which property blocks to search
            blocks_to_search = {};

            % Add the schema's classname block
            if isfield(doc_struct, schema.classname)
                blocks_to_search{end+1} = schema.classname;
            end

            % Add superclass classname blocks
            if ~isempty(schema.superclasses)
                supers = schema.superclasses;
                if isstruct(supers)
                    for i = 1:numel(supers)
                        sc_name = supers(i).classname;
                        if isfield(doc_struct, sc_name)
                            blocks_to_search{end+1} = sc_name; %#ok<AGROW>
                        end
                    end
                elseif iscell(supers)
                    for i = 1:numel(supers)
                        sc = supers{i};
                        if isstruct(sc) && isfield(sc, 'classname')
                            sc_name = sc.classname;
                        elseif isa(sc, 'did.schema.Schema')
                            sc_name = sc.classname;
                        else
                            continue;
                        end
                        if isfield(doc_struct, sc_name)
                            blocks_to_search{end+1} = sc_name; %#ok<AGROW>
                        end
                    end
                end
            end

            % Search through all blocks
            for i = 1:numel(blocks_to_search)
                block = doc_struct.(blocks_to_search{i});
                if isstruct(block) && isfield(block, field_name)
                    value = block.(field_name);
                    return;
                end
            end

            value = sentinel;
        end

    end

end
