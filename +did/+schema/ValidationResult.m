classdef ValidationResult
% VALIDATIONRESULT A simple result object returned by all validation functions.
%   Holds validation status, error messages, warnings, and the field path
%   where a failure occurred.
%
%   r = did.schema.ValidationResult()          — constructs a passing result
%   r = did.schema.ValidationResult(errors)    — constructs a failing result

    properties
        is_valid    (1,1) logical  = true    % true if validation passed
        errors      cell           = {}      % error messages; empty if is_valid
        warnings    cell           = {}      % warnings (e.g., default_value doesn't pass)
        field_path  char           = ''      % dot-separated path to the field that failed
    end

    methods

        function obj = ValidationResult(errors)
            % VALIDATIONRESULT Construct a validation result.
            %   r = ValidationResult()        — passing result
            %   r = ValidationResult(errors)  — failing result with error messages
            if nargin > 0 && ~isempty(errors)
                if ischar(errors)
                    errors = {errors};
                end
                obj.errors = errors;
                obj.is_valid = false;
            end
        end

        function obj = add_error(obj, message)
            % ADD_ERROR Append an error message and mark result as invalid.
            %   r = r.add_error('Some error message')
            obj.errors{end+1} = char(message);
            obj.is_valid = false;
        end

        function obj = add_warning(obj, message)
            % ADD_WARNING Append a warning message (does not affect is_valid).
            %   r = r.add_warning('Some warning message')
            obj.warnings{end+1} = char(message);
        end

        function obj = merge(obj, other)
            % MERGE Combine two ValidationResult objects.
            %   r2 = r.merge(other_result)
            %   Union of errors and warnings from both results.
            if ~isa(other, 'did.schema.ValidationResult')
                error('did:schema:ValidationResult:InvalidInput', ...
                    'merge requires a did.schema.ValidationResult object.');
            end
            obj.errors = [obj.errors, other.errors];
            obj.warnings = [obj.warnings, other.warnings];
            if ~other.is_valid
                obj.is_valid = false;
            end
            % Keep field_path from the first result if set, otherwise use other's
            if isempty(obj.field_path) && ~isempty(other.field_path)
                obj.field_path = other.field_path;
            end
        end

        function disp(obj)
            % DISP Pretty-print the validation result.
            if obj.is_valid
                fprintf('  ValidationResult: VALID\n');
            else
                fprintf('  ValidationResult: INVALID\n');
            end
            if ~isempty(obj.field_path)
                fprintf('  Field path: %s\n', obj.field_path);
            end
            if ~isempty(obj.errors)
                fprintf('  Errors (%d):\n', numel(obj.errors));
                for i = 1:numel(obj.errors)
                    fprintf('    - %s\n', obj.errors{i});
                end
            end
            if ~isempty(obj.warnings)
                fprintf('  Warnings (%d):\n', numel(obj.warnings));
                for i = 1:numel(obj.warnings)
                    fprintf('    - %s\n', obj.warnings{i});
                end
            end
        end

    end

end
