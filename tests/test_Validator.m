classdef test_Validator < matlab.unittest.TestCase
% TEST_VALIDATOR Unit tests for did.schema.Validator class.

    methods (Test)

        %% check_mustBeNonEmpty tests

        function test_mustBeNonEmpty_empty_string_fails(testCase)
            testCase.verifyFalse(did.schema.Validator.check_mustBeNonEmpty(''));
        end

        function test_mustBeNonEmpty_empty_array_fails(testCase)
            testCase.verifyFalse(did.schema.Validator.check_mustBeNonEmpty([]));
        end

        function test_mustBeNonEmpty_empty_cell_fails(testCase)
            testCase.verifyFalse(did.schema.Validator.check_mustBeNonEmpty({}));
        end

        function test_mustBeNonEmpty_empty_struct_fails(testCase)
            testCase.verifyFalse(did.schema.Validator.check_mustBeNonEmpty(struct()));
        end

        function test_mustBeNonEmpty_string_passes(testCase)
            testCase.verifyTrue(did.schema.Validator.check_mustBeNonEmpty('hello'));
        end

        function test_mustBeNonEmpty_number_passes(testCase)
            testCase.verifyTrue(did.schema.Validator.check_mustBeNonEmpty(1));
        end

        function test_mustBeNonEmpty_struct_with_fields_passes(testCase)
            testCase.verifyTrue(did.schema.Validator.check_mustBeNonEmpty(struct('a', 1)));
        end

        %% check_mustBeScalar tests

        function test_mustBeScalar_vector_fails(testCase)
            testCase.verifyFalse(did.schema.Validator.check_mustBeScalar([1 2 3]));
        end

        function test_mustBeScalar_scalar_passes(testCase)
            testCase.verifyTrue(did.schema.Validator.check_mustBeScalar(1));
        end

        function test_mustBeScalar_string_passes(testCase)
            testCase.verifyTrue(did.schema.Validator.check_mustBeScalar('hi'));
        end

        %% check_mustNotHaveNaN tests

        function test_mustNotHaveNaN_nan_fails(testCase)
            testCase.verifyFalse(did.schema.Validator.check_mustNotHaveNaN(NaN));
        end

        function test_mustNotHaveNaN_array_with_nan_fails(testCase)
            testCase.verifyFalse(did.schema.Validator.check_mustNotHaveNaN([1 NaN 3]));
        end

        function test_mustNotHaveNaN_number_passes(testCase)
            testCase.verifyTrue(did.schema.Validator.check_mustNotHaveNaN(1.5));
        end

        function test_mustNotHaveNaN_array_passes(testCase)
            testCase.verifyTrue(did.schema.Validator.check_mustNotHaveNaN([1 2 3]));
        end

        %% check_timestamp tests

        function test_timestamp_valid_passes(testCase)
            testCase.verifyTrue(did.schema.Validator.check_timestamp('2024-06-01T12:00:00.000Z'));
        end

        function test_timestamp_invalid_fails(testCase)
            testCase.verifyFalse(did.schema.Validator.check_timestamp('not-a-date'));
        end

        function test_timestamp_empty_fails(testCase)
            testCase.verifyFalse(did.schema.Validator.check_timestamp(''));
        end

        %% check_type tests

        function test_check_type_did_uid(testCase)
            testCase.verifyTrue(did.schema.Validator.check_type('abc123', 'did_uid'));
            testCase.verifyFalse(did.schema.Validator.check_type(123, 'did_uid'));
        end

        function test_check_type_char(testCase)
            testCase.verifyTrue(did.schema.Validator.check_type('hello', 'char'));
            testCase.verifyFalse(did.schema.Validator.check_type(123, 'char'));
        end

        function test_check_type_string_alias(testCase)
            testCase.verifyTrue(did.schema.Validator.check_type('hello', 'string'));
        end

        function test_check_type_integer(testCase)
            testCase.verifyTrue(did.schema.Validator.check_type(42, 'integer'));
            testCase.verifyFalse(did.schema.Validator.check_type('nope', 'integer'));
        end

        function test_check_type_double(testCase)
            testCase.verifyTrue(did.schema.Validator.check_type(3.14, 'double'));
            testCase.verifyFalse(did.schema.Validator.check_type('nope', 'double'));
        end

        function test_check_type_matrix(testCase)
            testCase.verifyTrue(did.schema.Validator.check_type([1 2; 3 4], 'matrix'));
            testCase.verifyFalse(did.schema.Validator.check_type('nope', 'matrix'));
        end

        function test_check_type_timestamp(testCase)
            testCase.verifyTrue(did.schema.Validator.check_type('2024-01-01T00:00:00Z', 'timestamp'));
            testCase.verifyFalse(did.schema.Validator.check_type(123, 'timestamp'));
        end

        function test_check_type_boolean(testCase)
            testCase.verifyTrue(did.schema.Validator.check_type(true, 'boolean'));
            testCase.verifyFalse(did.schema.Validator.check_type('nope', 'boolean'));
        end

        function test_check_type_structure(testCase)
            testCase.verifyTrue(did.schema.Validator.check_type(struct('a', 1), 'structure'));
            testCase.verifyFalse(did.schema.Validator.check_type('nope', 'structure'));
        end

        %% check_constraints tests

        function test_constraints_integer_min_max(testCase)
            c = struct('min', 0, 'max', 100);
            testCase.verifyTrue(did.schema.Validator.check_constraints(50, 'integer', c));
            testCase.verifyFalse(did.schema.Validator.check_constraints(-1, 'integer', c));
            testCase.verifyFalse(did.schema.Validator.check_constraints(101, 'integer', c));
        end

        function test_constraints_double_min_max(testCase)
            c = struct('min', 0.0, 'max', 1.0);
            testCase.verifyTrue(did.schema.Validator.check_constraints(0.5, 'double', c));
            testCase.verifyFalse(did.schema.Validator.check_constraints(-0.1, 'double', c));
            testCase.verifyFalse(did.schema.Validator.check_constraints(1.1, 'double', c));
        end

        function test_constraints_char_max_length(testCase)
            c = struct('max_length', 5);
            testCase.verifyTrue(did.schema.Validator.check_constraints('abc', 'char', c));
            testCase.verifyFalse(did.schema.Validator.check_constraints('abcdef', 'char', c));
        end

        function test_constraints_matrix_rows_cols(testCase)
            c = struct('rows', 2, 'cols', 3, 'min', [], 'max', []);
            testCase.verifyTrue(did.schema.Validator.check_constraints([1 2 3; 4 5 6], 'matrix', c));
            testCase.verifyFalse(did.schema.Validator.check_constraints([1 2; 3 4; 5 6], 'matrix', c));
        end

        %% parse_semver tests

        function test_parse_semver_valid(testCase)
            [major, minor, patch] = did.schema.Validator.parse_semver('1.2.3');
            testCase.verifyEqual(major, 1);
            testCase.verifyEqual(minor, 2);
            testCase.verifyEqual(patch, 3);
        end

        function test_parse_semver_invalid(testCase)
            testCase.verifyError( ...
                @() did.schema.Validator.parse_semver('bad'), ...
                'did:schema:semver:InvalidFormat');
        end

        %% is_compatible_version tests

        function test_compatible_version_same_major(testCase)
            testCase.verifyTrue( ...
                did.schema.Validator.is_compatible_version('1.0.0', '1.2.3'));
        end

        function test_incompatible_version_different_major(testCase)
            testCase.verifyFalse( ...
                did.schema.Validator.is_compatible_version('1.0.0', '2.0.0'));
        end

    end

end
