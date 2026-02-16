classdef test_MetaValidator < matlab.unittest.TestCase
% TEST_METAVALIDATOR Unit tests for did.schema.MetaValidator class.

    properties
        repo_root
        schema_dir
        fixtures_dir
    end

    methods (TestMethodSetup)
        function setup(testCase)
            testCase.repo_root = fileparts(fileparts(mfilename('fullpath')));
            testCase.schema_dir = fullfile(testCase.repo_root, 'schemas');
            testCase.fixtures_dir = fullfile(testCase.repo_root, 'tests', 'fixtures');
        end
    end

    methods (Test)

        function test_base_schema_passes(testCase)
            % Test that base_schema.json passes meta-validation.
            schema_path = fullfile(testCase.schema_dir, 'base_schema.json');
            result = did.schema.MetaValidator.validate(schema_path);
            testCase.verifyTrue(result.is_valid, ...
                sprintf('Errors: %s', strjoin(result.errors, '; ')));
        end

        function test_probe_location_schema_passes(testCase)
            % Test that probe_location_schema.json passes meta-validation.
            schema_path = fullfile(testCase.schema_dir, 'probe', 'probe_location_schema.json');
            result = did.schema.MetaValidator.validate(schema_path);
            testCase.verifyTrue(result.is_valid, ...
                sprintf('Errors: %s', strjoin(result.errors, '; ')));
        end

        function test_missing_classname_fails(testCase)
            % Test that invalid_schema_missing_classname.json fails meta-validation.
            fixture_path = fullfile(testCase.fixtures_dir, 'invalid_schema_missing_classname.json');
            result = did.schema.MetaValidator.validate(fixture_path);
            testCase.verifyFalse(result.is_valid);
        end

        function test_unrecognized_type_fails(testCase)
            % Test that a schema with an unrecognized type string fails meta-validation.
            bad_schema = struct( ...
                'classname', 'test_bad_type', ...
                'class_version', '1.0.0', ...
                'superclasses', {{}}, ...
                'depends_on', {{}}, ...
                'file', {{}}, ...
                'fields', {{struct( ...
                    'name', 'bad_field', ...
                    'type', 'nonexistent_type', ...
                    'blank_value', '', ...
                    'default_value', '', ...
                    'mustBeNonEmpty', false, ...
                    'mustBeScalar', true, ...
                    'mustNotHaveNaN', false, ...
                    'queryable', false, ...
                    'ontology', [], ...
                    'documentation', 'A field with bad type.', ...
                    'constraints', struct())}});
            result = did.schema.MetaValidator.validate(bad_schema);
            testCase.verifyFalse(result.is_valid);
        end

    end

end
