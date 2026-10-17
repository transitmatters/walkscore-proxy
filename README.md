# Walkscore® Proxy

Call the Walkscore® API for a specific MBTA stop, and return it's walkscore®

Requires a Walkscore® API key, which you can get from their [site](https://www.walkscore.com/professional/api.php).

## Example Call
```
/api/walkscore/place-NHRML-0152
```

```
{
  ...
  "bike": {
    "description": "Somewhat Bikeable",
    "score": 39
  },
  "description": "Somewhat Walkable",
  "walkscore": 54,
  ...
}
```

## Development

- Requires Python 3.14 (with [mise](https://mise.jdx.dev): `mise trust && mise install`, pinned in `.python-version`)
- Requires [uv](https://docs.astral.sh/uv/)

Install dependencies and the pre-commit hook
```
uv sync
uv run pre-commit install
```

Run
```
cd server && uv run chalice local --port=5000
```
to test

Lint and format
```
uv run ruff check .
uv run ruff format .
```
