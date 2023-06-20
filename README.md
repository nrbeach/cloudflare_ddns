# Cloudflare DDNS

---

Inspired by [https://github.com/mirioeggmann/cloudflare-ddns](https://github.com/mirioeggmann/cloudflare-ddns)

I've modified this slightly more towards my workflow, i.e. managing multiple hosted domains/sub-domains in one cronjob.

Usage:
`cloudflare_ddns.py` accepts a JSON blob at the command line that provides the necessary details for the Cloudflare API.

`# cloudflare_ddns.py '{"1234567": [{"record_id": "11111111", name: "foo.com", "proxied": true}]}'`

```json
{
  "zone_id_1234": [
    {
      "record_id": "11111111",
      "name": "bar.com",
      "proxied": true
    },
    {
      "record_id": "22222222",
      "name": "foo.bar.com",
      "proxied": false
    }
  ],
  "zone_id_5678": [
    {
      "record_id": "33333333",
      "name": "foo.com",
      "proxied": false
    }
  ]
}
```
