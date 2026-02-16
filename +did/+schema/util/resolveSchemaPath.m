function resolved = resolveSchemaPath(path_with_tokens, token_map)
% RESOLVESCHEMAPATH Substitute path tokens in a schema path string.
%   resolved = resolveSchemaPath('$NDISCHEMAPATH/base_schema.json', token_map)
%   token_map : struct where fieldnames are token names (without $),
%               and values are the replacement path strings.
%   Example:
%     token_map.NDISCHEMAPATH = '/home/user/schemas';
%     resolveSchemaPath('$NDISCHEMAPATH/base.json', token_map)
%     -> '/home/user/schemas/base.json'

    if nargin < 2
        token_map = struct();
    end

    if ~ischar(path_with_tokens) && ~isstring(path_with_tokens)
        error('did:schema:resolveSchemaPath:InvalidInput', ...
            'path_with_tokens must be a character vector or string.');
    end

    resolved = char(path_with_tokens);

    if isstruct(token_map)
        token_names = fieldnames(token_map);
        for i = 1:numel(token_names)
            token = token_names{i};
            replacement = char(token_map.(token));
            % Remove trailing file separators from replacement
            while ~isempty(replacement) && (replacement(end) == '/' || replacement(end) == '\')
                replacement = replacement(1:end-1);
            end
            resolved = strrep(resolved, ['$' token], replacement);
        end
    end

end
