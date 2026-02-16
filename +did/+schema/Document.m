classdef Document
% DOCUMENT Loads and represents a DID/NDI document instance.
%   A document is an instance of a schema-defined document type. It holds
%   data and can be validated against its schema.
%
%   d = did.schema.Document(definition_path_or_struct)
%   d = did.schema.Document(definition_path_or_struct, schema_search_paths)
%
% TODO: Dependency existence checks (verifying that depends_on values
% point to real documents in a database) are not implemented at this
% layer. This layer only checks that mustBeNonEmpty dependencies have
% non-empty values. Full existence checking is the responsibility of
% the database layer.
%
%   See also: did.schema.Schema, did.schema.Validator, did.schema.ValidationResult

    properties (SetAccess = private)
        classname       char                = ''     % document type name
        class_version   char                = ''     % semver string
        schema                                       % did.schema.Schema for this document
        data            struct                       % the full document data
        definition_path char                = ''     % path to the definition file
    end

    properties (Access = private)
        path_tokens     struct              = struct()
    end

    methods

        function obj = Document(definition_path_or_struct, schema_search_paths)
            % DOCUMENT Construct a Document by loading a definition file or struct.
            %   d = did.schema.Document(definition_path_or_struct)
            %   d = did.schema.Document(definition_path_or_struct, schema_search_paths)
            %
            %   definition_path_or_struct : path to a definition JSON file, or
            %                               a struct already loaded from one
            %   schema_search_paths       : (optional) struct with token -> path
            %                               mappings for resolving schema paths

            if nargin < 1
                error('did:schema:Document:NoInput', ...
                    'A definition path or struct is required.');
            end

            if nargin >= 2 && isstruct(schema_search_paths)
                obj.path_tokens = schema_search_paths;
            end

            % Load document data
            if ischar(definition_path_or_struct) || isstring(definition_path_or_struct)
                obj.definition_path = char(definition_path_or_struct);
                obj.data = did.schema.util.loadJSON(obj.definition_path);
            elseif isstruct(definition_path_or_struct)
                obj.data = definition_path_or_struct;
                obj.definition_path = '';
            else
                error('did:schema:Document:InvalidInput', ...
                    'Input must be a file path or struct.');
            end

            % Extract document class information
            if isfield(obj.data, 'document_class')
                dc = obj.data.document_class;
                if isfield(dc, 'classname')
                    obj.classname = char(dc.classname);
                end
                if isfield(dc, 'class_version')
                    obj.class_version = char(dc.class_version);
                end

                % Load the schema
                if isfield(dc, 'schema')
                    schema_path = char(dc.schema);
                    resolved_schema = did.schema.util.resolveSchemaPath( ...
                        schema_path, obj.path_tokens);
                    try
                        obj.schema = did.schema.Schema(resolved_schema, obj.path_tokens);
                    catch me
                        warning('did:schema:Document:SchemaLoadFailed', ...
                            'Could not load schema "%s": %s', ...
                            resolved_schema, me.message);
                        obj.schema = [];
                    end
                end
            end
        end

        function result = validate(obj)
            % VALIDATE Validate this document against its schema.
            %   result = d.validate()
            %   Returns a did.schema.ValidationResult object.

            if isempty(obj.schema)
                result = did.schema.ValidationResult();
                result = result.add_error('No schema loaded for validation.');
                return;
            end

            result = did.schema.Validator.validate_document(obj.data, obj.schema);
        end

        function value = get(obj, field_name)
            % GET Return the value of a named field, searching all property blocks.
            %   value = d.get(field_name)

            field_name = char(field_name);

            % Search through all struct fields in the document data
            top_fields = fieldnames(obj.data);
            for i = 1:numel(top_fields)
                block_name = top_fields{i};
                block = obj.data.(block_name);
                if isstruct(block) && isfield(block, field_name)
                    value = block.(field_name);
                    return;
                end
            end

            error('did:schema:Document:FieldNotFound', ...
                'Field "%s" not found in document.', field_name);
        end

        function d2 = set(obj, field_name, value)
            % SET Return a new Document with the named field set to value.
            %   d2 = d.set(field_name, value)
            %   Does not mutate the original.

            field_name = char(field_name);
            new_data = obj.data;

            % Search through all struct fields to find which block contains the field
            top_fields = fieldnames(new_data);
            found = false;
            for i = 1:numel(top_fields)
                block_name = top_fields{i};
                block = new_data.(block_name);
                if isstruct(block) && isfield(block, field_name)
                    new_data.(block_name).(field_name) = value;
                    found = true;
                    break;
                end
            end

            if ~found
                error('did:schema:Document:FieldNotFound', ...
                    'Field "%s" not found in document.', field_name);
            end

            % Construct a new Document from the modified data
            d2 = did.schema.Document(new_data, obj.path_tokens);
        end

        function s = to_struct(obj)
            % TO_STRUCT Return the document as a plain MATLAB struct.
            %   s = d.to_struct()
            s = obj.data;
        end

        function json = to_json(obj)
            % TO_JSON Return the document as a JSON string.
            %   json = d.to_json()
            json = jsonencode(obj.data, 'PrettyPrint', true);
        end

    end

end
