classdef test_Document < matlab.unittest.TestCase
% TEST_DOCUMENT Unit tests for did.schema.Document class.

    properties
        repo_root
        schema_dir
        definitions_dir
        fixtures_dir
        path_tokens
    end

    methods (TestMethodSetup)
        function setup(testCase)
            testCase.repo_root = fileparts(fileparts(mfilename('fullpath')));
            testCase.schema_dir = fullfile(testCase.repo_root, 'schemas');
            testCase.definitions_dir = fullfile(testCase.repo_root, 'definitions');
            testCase.fixtures_dir = fullfile(testCase.repo_root, 'tests', 'fixtures');
            testCase.path_tokens = struct( ...
                'NDISCHEMAPATH', testCase.schema_dir, ...
                'NDIDOCUMENTPATH', testCase.definitions_dir);
        end
    end

    methods (Test)

        function test_valid_base_document_loads_and_validates(testCase)
            % Test that valid_base_document.json loads and validates cleanly.
            doc_path = fullfile(testCase.fixtures_dir, 'valid_base_document.json');
            d = did.schema.Document(doc_path, testCase.path_tokens);
            result = d.validate();
            testCase.verifyTrue(result.is_valid, ...
                sprintf('Errors: %s', strjoin(result.errors, '; ')));
        end

        function test_valid_probe_location_loads_and_validates(testCase)
            % Test that valid_probe_location_document.json loads and validates.
            doc_path = fullfile(testCase.fixtures_dir, 'valid_probe_location_document.json');
            d = did.schema.Document(doc_path, testCase.path_tokens);
            result = d.validate();
            testCase.verifyTrue(result.is_valid, ...
                sprintf('Errors: %s', strjoin(result.errors, '; ')));
        end

        function test_invalid_missing_id(testCase)
            % Test that invalid_base_document_missing_id.json fails validation
            % with an error mentioning "id".
            doc_path = fullfile(testCase.fixtures_dir, 'invalid_base_document_missing_id.json');
            d = did.schema.Document(doc_path, testCase.path_tokens);
            result = d.validate();
            testCase.verifyFalse(result.is_valid);
            % Check that at least one error mentions "id"
            has_id_error = false;
            for i = 1:numel(result.errors)
                if contains(result.errors{i}, 'id')
                    has_id_error = true;
                    break;
                end
            end
            testCase.verifyTrue(has_id_error, ...
                'Expected an error mentioning "id".');
        end

        function test_invalid_bad_datestamp(testCase)
            % Test that invalid_base_document_bad_datestamp.json fails validation
            % with an error mentioning "datestamp".
            doc_path = fullfile(testCase.fixtures_dir, 'invalid_base_document_bad_datestamp.json');
            d = did.schema.Document(doc_path, testCase.path_tokens);
            result = d.validate();
            testCase.verifyFalse(result.is_valid);
            % Check that at least one error mentions "datestamp"
            has_datestamp_error = false;
            for i = 1:numel(result.errors)
                if contains(result.errors{i}, 'datestamp')
                    has_datestamp_error = true;
                    break;
                end
            end
            testCase.verifyTrue(has_datestamp_error, ...
                'Expected an error mentioning "datestamp".');
        end

        function test_get_field_value(testCase)
            % Test that Document.get('id') returns the correct value.
            doc_path = fullfile(testCase.fixtures_dir, 'valid_base_document.json');
            d = did.schema.Document(doc_path, testCase.path_tokens);
            id_val = d.get('id');
            testCase.verifyEqual(id_val, '4126919195e6b5af_40d651024919a2e4');
        end

        function test_set_field_value(testCase)
            % Test that Document.set('name', 'new_name') returns a new document
            % with the updated value and does not modify the original.
            doc_path = fullfile(testCase.fixtures_dir, 'valid_base_document.json');
            d = did.schema.Document(doc_path, testCase.path_tokens);
            original_name = d.get('name');

            d2 = d.set('name', 'new_name');
            testCase.verifyEqual(d2.get('name'), 'new_name');
            testCase.verifyEqual(d.get('name'), original_name, ...
                'Original document should not be modified.');
        end

    end

end
