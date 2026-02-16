classdef test_Schema < matlab.unittest.TestCase
% TEST_SCHEMA Unit tests for did.schema.Schema class.

    properties
        repo_root
        schema_dir
        fixtures_dir
        path_tokens
    end

    methods (TestMethodSetup)
        function setup(testCase)
            testCase.repo_root = fileparts(fileparts(mfilename('fullpath')));
            testCase.schema_dir = fullfile(testCase.repo_root, 'schemas');
            testCase.fixtures_dir = fullfile(testCase.repo_root, 'tests', 'fixtures');
            testCase.path_tokens = struct( ...
                'NDISCHEMAPATH', testCase.schema_dir, ...
                'NDIDOCUMENTPATH', fullfile(testCase.repo_root, 'definitions'));
        end
    end

    methods (Test)

        function test_valid_schema_loads(testCase)
            % Test that a valid schema file loads without error.
            schema_path = fullfile(testCase.schema_dir, 'base_schema.json');
            s = did.schema.Schema(schema_path, testCase.path_tokens);
            testCase.verifyNotEmpty(s);
            testCase.verifyEqual(s.classname, 'base');
        end

        function test_base_schema_field_count(testCase)
            % Test that Schema.fields contains the correct number of fields
            % for base_schema.json (4 fields: id, session_id, name, datestamp).
            schema_path = fullfile(testCase.schema_dir, 'base_schema.json');
            s = did.schema.Schema(schema_path, testCase.path_tokens);

            if isstruct(s.fields)
                n_fields = numel(s.fields);
            elseif iscell(s.fields)
                n_fields = numel(s.fields);
            else
                n_fields = 0;
            end
            testCase.verifyEqual(n_fields, 4);
        end

        function test_probe_location_all_fields(testCase)
            % Test that Schema.all_fields for probe_location includes both
            % base and probe_location fields (4 base + 2 probe_location = 6).
            schema_path = fullfile(testCase.schema_dir, 'probe', 'probe_location_schema.json');
            s = did.schema.Schema(schema_path, testCase.path_tokens);

            if isstruct(s.all_fields)
                n_all = numel(s.all_fields);
            elseif iscell(s.all_fields)
                n_all = numel(s.all_fields);
            else
                n_all = 0;
            end
            testCase.verifyEqual(n_all, 6);
        end

        function test_bad_path_throws(testCase)
            % Test that loading a schema with a bad path throws a clear error.
            testCase.verifyError( ...
                @() did.schema.Schema('/nonexistent/path/schema.json'), ...
                'did:schema:Schema:FileNotFound');
        end

        function test_validate_schema_file_valid(testCase)
            % Test that validate_schema_file() returns is_valid = true for
            % base_schema.json.
            schema_path = fullfile(testCase.schema_dir, 'base_schema.json');
            s = did.schema.Schema(schema_path, testCase.path_tokens);
            result = s.validate_schema_file();
            testCase.verifyTrue(result.is_valid);
        end

        function test_validate_schema_file_invalid(testCase)
            % Test that validate_schema_file() returns is_valid = false for
            % invalid_schema_missing_classname.json.
            fixture_path = fullfile(testCase.fixtures_dir, 'invalid_schema_missing_classname.json');
            % Load the invalid schema as raw struct to test via MetaValidator
            raw = did.schema.util.loadJSON(fixture_path);
            result = did.schema.MetaValidator.validate(raw);
            testCase.verifyFalse(result.is_valid);
        end

    end

end
