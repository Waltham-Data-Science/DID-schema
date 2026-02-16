function s = loadJSON(filepath)
% LOADJSON Read a JSON file and return it as a MATLAB struct.
%   s = loadJSON(filepath)
%   filepath : absolute or relative path to a .json file
%   s        : MATLAB struct (or cell array for JSON arrays)
%
% Uses jsondecode internally. Throws a clear error if the file does not
% exist or is not valid JSON.

    if ~ischar(filepath) && ~isstring(filepath)
        error('did:schema:loadJSON:InvalidInput', ...
            'filepath must be a character vector or string.');
    end

    filepath = char(filepath);

    if ~exist(filepath, 'file')
        error('did:schema:loadJSON:FileNotFound', ...
            'JSON file not found: %s', filepath);
    end

    try
        text = fileread(filepath);
    catch me
        error('did:schema:loadJSON:ReadError', ...
            'Could not read file "%s": %s', filepath, me.message);
    end

    if isempty(strtrim(text))
        error('did:schema:loadJSON:EmptyFile', ...
            'JSON file is empty: %s', filepath);
    end

    try
        s = jsondecode(text);
    catch me
        error('did:schema:loadJSON:ParseError', ...
            'Invalid JSON in file "%s": %s', filepath, me.message);
    end

end
