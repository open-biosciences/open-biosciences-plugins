# MCP Token Budgeting (`slim` Parameter)

All MCP tools in the biosciences gateway support a `slim` parameter for token-efficient queries.

## When to Use `slim=true`

- **LOCATE phase**: Fast candidate lists (returns ~20 tokens/entity vs ~115-300 tokens)
- **Batch operations**: Resolving multiple entities in a single turn
- **Exploration**: Quick overviews without full metadata

## When to Use `slim=false` (default)

- **RETRIEVE phase**: Need full metadata with cross-references
- **Validation**: Verifying detailed properties
- **Graph persistence**: Collecting complete entity records

## Example

```
# LOCATE: Find top 10 gene candidates (slim=true for speed)
Call `biosciences-mcp:hgnc_search_genes` with: {"query": "TNF", "slim": true, "page_size": 10}
→ Returns minimal fields: ID, symbol, name only (~20 tokens each)

# RETRIEVE: Get full record for validation (slim=false, default)
Call `biosciences-mcp:hgnc_get_gene` with: {"hgnc_id": "HGNC:11892"}
→ Returns complete metadata with cross-references (~115 tokens)
```

## Impact

Using `slim=true` during LOCATE enables 5-10x more entities per LLM turn without context overflow.

## Reference

This token budgeting pattern is detailed in `reference/prior-art-api-patterns.md` (Section 7.1).
