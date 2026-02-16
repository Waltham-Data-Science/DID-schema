function [major, minor, patch] = semver(version_string)
% SEMVER Parse a semantic version string.
%   [major, minor, patch] = semver('1.2.3')
%   Throws an error if the string does not match \d+\.\d+\.\d+.

    if ~ischar(version_string) && ~isstring(version_string)
        error('did:schema:semver:InvalidInput', ...
            'version_string must be a character vector or string.');
    end

    version_string = char(version_string);

    tokens = regexp(version_string, '^\s*(\d+)\.(\d+)\.(\d+)\s*$', 'tokens');

    if isempty(tokens)
        error('did:schema:semver:InvalidFormat', ...
            'Invalid semver string: "%s". Expected format: MAJOR.MINOR.PATCH (e.g., "1.2.3").', ...
            version_string);
    end

    parts = tokens{1};
    major = str2double(parts{1});
    minor = str2double(parts{2});
    patch = str2double(parts{3});

end
