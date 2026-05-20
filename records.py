def filter_rows(rows, term):
    """Return rows where any of the first 13 columns contains term (case-insensitive)."""
    if not term:
        return list(rows)
    term = term.lower()
    return [r for r in rows if any(term in str(v).lower() for v in r[:13])]


def sort_rows(rows, col_idx, ascending=True):
    """Return rows sorted by col_idx, with numeric-aware comparison."""
    def _key(r):
        v = r[col_idx]
        try:
            return (0, int(v))
        except (ValueError, TypeError):
            return (1, str(v).lower())
    return sorted(rows, key=_key, reverse=not ascending)
