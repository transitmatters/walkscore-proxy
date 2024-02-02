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

- Requires Python 3.11

Run
```
poetry run chalice local --port=5000
```
to test
