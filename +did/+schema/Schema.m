classdef Schema
% SCHEMA Loads and represents a single DID/NDI schema file.
%   Loads, parses, and validates schema files. Resolves superclass
%   inheritance and provides access to all fields (own + inherited).
%
%   s = did.schema.Schema(schema_path)
%   s = did.schema.Schema(schema_path, path_tokens)
%
% TODO: Superclass schemas are resolved relative to the referencing
% schema's directory. Cross-repo superclass resolution (e.g., NDI schema
% depending on a DID schema in a different repo) is not yet implemented
% — path tokens are the interim mechanism.
%
%   See also: did.schema.Document, did.schema.Validator, did.schema.MetaValidator

    properties (SetAccess = private)
        classname       char           = ''     % document type name
        class_version   char           = ''     % semver string
        superclasses                   = []     % loaded superclass schemas (recursive)
        depends_on                     = []     % dependency definitions
        file                           = []     % file record definitions
        fields                         = []     % field definitions for this class only
        all_fields                     = []     % fields from this class + all superclasses
        schema_path     char           = ''     % resolved filesystem path to this schema file
        raw             struct                  % the raw parsed JSON struct
    end

    properties (Access = private)
        path_tokens     struct         = struct() % token -> path mappings
    end

    methods

        function obj = Schema(schema_path, path_tokens)
            % SCHEMA Construct a Schema object by loading a schema file.
            %   s = did.schema.Schema(schema_path)
            %   s = did.schema.Schema(schema_path, path_tokens)
            %
            %   schema_path  : path to the schema JSON file; may contain
            %                  tokens like $NDISCHEMAPATH
            %   path_tokens  : (optional) struct with token -> path mappings
            %                  e.g., struct('NDISCHEMAPATH', '/path/to/schemas')

            if nargin < 1
                error('did:schema:Schema:NoInput', ...
                    'A schema path is required.');
            end

            if nargin >= 2
                obj.path_tokens = path_tokens;
            end

            % Resolve tokens in path
            resolved = did.schema.util.resolveSchemaPath(schema_path, obj.path_tokens);
            obj.schema_path = resolved;

            % Load the schema file
            if ~exist(resolved, 'file')
                error('did:schema:Schema:FileNotFound', ...
                    'Schema file not found: %s', resolved);
            end

            raw_data = did.schema.util.loadJSON(resolved);
            obj.raw = raw_data;

            % Extract top-level properties
            obj.classname = char(raw_data.classname);
            obj.class_version = char(raw_data.class_version);

            % Extract depends_on
            if isfield(raw_data, 'depends_on') && ~isempty(raw_data.depends_on)
                obj.depends_on = raw_data.depends_on;
            else
                obj.depends_on = [];
            end

            % Extract file records
            if isfield(raw_data, 'file') && ~isempty(raw_data.file)
                obj.file = raw_data.file;
            else
                obj.file = [];
            end

            % Extract fields
            if isfield(raw_data, 'fields') && ~isempty(raw_data.fields)
                obj.fields = raw_data.fields;
            else
                obj.fields = [];
            end

            % Resolve superclass schemas
            obj.superclasses = obj.resolve_superclasses(raw_data);

            % Build all_fields (superclass-first order)
            obj.all_fields = obj.build_all_fields();
        end

        function result = validate_schema_file(obj)
            % VALIDATE_SCHEMA_FILE Validate this schema file against the meta-schema.
            %   result = s.validate_schema_file()
            %   Returns a did.schema.ValidationResult object.

            result = did.schema.MetaValidator.validate(obj.raw);
        end

        function result = validate_document(obj, doc_struct)
            % VALIDATE_DOCUMENT Validate a document struct against this schema.
            %   result = s.validate_document(doc_struct)
            %   Validates all fields, including superclass fields.
            %   Returns a did.schema.ValidationResult object.

            result = did.schema.Validator.validate_document(doc_struct, obj);
        end

        function field = get_field(obj, field_name)
            % GET_FIELD Return the field definition struct for a named field.
            %   field = s.get_field(field_name)
            %   Searches this class's fields and all inherited fields.
            %   Returns empty struct if not found.

            field = struct();
            all_f = obj.all_fields;

            if isempty(all_f)
                return;
            end

            if isstruct(all_f)
                field_list = num2cell(all_f);
            elseif iscell(all_f)
                field_list = all_f;
            else
                return;
            end

            for i = 1:numel(field_list)
                if iscell(field_list)
                    f = field_list{i};
                else
                    f = field_list(i);
                end
                if isfield(f, 'name') && strcmp(char(f.name), char(field_name))
                    field = f;
                    return;
                end
            end
        end

        function disp(obj)
            % DISP Pretty-print the schema summary.
            fprintf('  did.schema.Schema\n');
            fprintf('    classname:     %s\n', obj.classname);
            fprintf('    class_version: %s\n', obj.class_version);
            fprintf('    schema_path:   %s\n', obj.schema_path);

            % Superclasses
            if ~isempty(obj.superclasses)
                if isstruct(obj.superclasses)
                    n_super = numel(obj.superclasses);
                elseif iscell(obj.superclasses)
                    n_super = numel(obj.superclasses);
                else
                    n_super = 0;
                end
                fprintf('    superclasses:  %d\n', n_super);
            else
                fprintf('    superclasses:  0\n');
            end

            % Fields
            n_own = did.schema.Schema.count_fields(obj.fields);
            n_all = did.schema.Schema.count_fields(obj.all_fields);
            fprintf('    fields (own):  %d\n', n_own);
            fprintf('    fields (all):  %d\n', n_all);

            % Dependencies
            if ~isempty(obj.depends_on)
                if isstruct(obj.depends_on)
                    n_deps = numel(obj.depends_on);
                elseif iscell(obj.depends_on)
                    n_deps = numel(obj.depends_on);
                else
                    n_deps = 0;
                end
            else
                n_deps = 0;
            end
            fprintf('    depends_on:    %d\n', n_deps);
        end

    end

    methods (Access = private)

        function supers = resolve_superclasses(obj, raw_data)
            % RESOLVE_SUPERCLASSES Load superclass schemas recursively.

            supers = [];

            if ~isfield(raw_data, 'superclasses') || isempty(raw_data.superclasses)
                return;
            end

            sc_refs = raw_data.superclasses;
            if isstruct(sc_refs)
                sc_list = num2cell(sc_refs);
            elseif iscell(sc_refs)
                sc_list = sc_refs;
            else
                return;
            end

            supers = {};
            schema_dir = fileparts(obj.schema_path);

            for i = 1:numel(sc_list)
                sc_ref = sc_list{i};
                sc_schema_path = char(sc_ref.schema);

                % Resolve tokens
                resolved_path = did.schema.util.resolveSchemaPath(sc_schema_path, obj.path_tokens);

                % If not absolute, resolve relative to this schema's directory
                if ~isAbsolutePath(resolved_path)
                    resolved_path = fullfile(schema_dir, resolved_path);
                end

                try
                    sc_schema = did.schema.Schema(resolved_path, obj.path_tokens);
                    supers{end+1} = sc_schema; %#ok<AGROW>
                catch me
                    warning('did:schema:Schema:SuperclassLoadFailed', ...
                        'Could not load superclass schema "%s": %s', ...
                        resolved_path, me.message);
                end
            end

            if isempty(supers)
                supers = [];
            end
        end

        function all_f = build_all_fields(obj)
            % BUILD_ALL_FIELDS Flatten fields from all superclasses + this class.
            %   Superclass-first order (base fields first).

            all_f = [];

            % Collect superclass fields first
            if ~isempty(obj.superclasses)
                if iscell(obj.superclasses)
                    sc_list = obj.superclasses;
                else
                    sc_list = {obj.superclasses};
                end

                for i = 1:numel(sc_list)
                    sc = sc_list{i};
                    if isa(sc, 'did.schema.Schema')
                        sc_fields = sc.all_fields;
                        all_f = did.schema.Schema.merge_fields(all_f, sc_fields);
                    end
                end
            end

            % Append this class's own fields
            all_f = did.schema.Schema.merge_fields(all_f, obj.fields);
        end

    end

    methods (Static, Access = private)

        function n = count_fields(fields)
            % COUNT_FIELDS Count the number of field definitions.
            if isempty(fields)
                n = 0;
            elseif isstruct(fields)
                n = numel(fields);
            elseif iscell(fields)
                n = numel(fields);
            else
                n = 0;
            end
        end

        function merged = merge_fields(existing, new_fields)
            % MERGE_FIELDS Append new fields to existing field list.
            %   Skips duplicates by name.

            if isempty(new_fields)
                merged = existing;
                return;
            end

            if isempty(existing)
                merged = new_fields;
                return;
            end

            % Convert to cell arrays for uniform handling
            if isstruct(existing)
                existing_list = num2cell(existing);
            elseif iscell(existing)
                existing_list = existing;
            else
                existing_list = {};
            end

            if isstruct(new_fields)
                new_list = num2cell(new_fields);
            elseif iscell(new_fields)
                new_list = new_fields;
            else
                new_list = {};
            end

            % Get existing field names
            existing_names = {};
            for i = 1:numel(existing_list)
                f = existing_list{i};
                if isstruct(f) && isfield(f, 'name')
                    existing_names{end+1} = char(f.name); %#ok<AGROW>
                end
            end

            % Append new fields, skipping duplicates
            for i = 1:numel(new_list)
                f = new_list{i};
                if isstruct(f) && isfield(f, 'name')
                    if ~ismember(char(f.name), existing_names)
                        existing_list{end+1} = f; %#ok<AGROW>
                        existing_names{end+1} = char(f.name); %#ok<AGROW>
                    end
                end
            end

            merged = existing_list;
        end

    end

end

function tf = isAbsolutePath(p)
    % ISABSOLUTEPATH Check if a path is absolute.
    p = char(p);
    if isempty(p)
        tf = false;
    elseif p(1) == '/' || p(1) == '\'
        tf = true;
    elseif length(p) >= 2 && p(2) == ':'
        tf = true; % Windows drive letter
    else
        tf = false;
    end
end
