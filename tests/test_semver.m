classdef test_semver < matlab.unittest.TestCase
% TEST_SEMVER Unit tests for did.schema.util.semver helper.

    methods (Test)

        function test_semver_1_0_0(testCase)
            % Test semver('1.0.0') returns [1, 0, 0].
            [major, minor, patch] = did.schema.util.semver('1.0.0');
            testCase.verifyEqual(major, 1);
            testCase.verifyEqual(minor, 0);
            testCase.verifyEqual(patch, 0);
        end

        function test_semver_2_14_3(testCase)
            % Test semver('2.14.3') returns [2, 14, 3].
            [major, minor, patch] = did.schema.util.semver('2.14.3');
            testCase.verifyEqual(major, 2);
            testCase.verifyEqual(minor, 14);
            testCase.verifyEqual(patch, 3);
        end

        function test_semver_bad_throws(testCase)
            % Test semver('bad') throws an error.
            testCase.verifyError( ...
                @() did.schema.util.semver('bad'), ...
                'did:schema:semver:InvalidFormat');
        end

        function test_semver_incomplete_throws(testCase)
            % Test semver('1.2') throws an error.
            testCase.verifyError( ...
                @() did.schema.util.semver('1.2'), ...
                'did:schema:semver:InvalidFormat');
        end

    end

end
