import json

from fastapi.responses import HTMLResponse

_MESSAGE_TYPE = "training-system-google-oauth"


class OAuthPopupResponse:
    @classmethod
    def success(cls, *, target_origin: str) -> HTMLResponse:
        return cls._build(target_origin=target_origin, succeeded=True, reason=None)

    @classmethod
    def error(cls, *, target_origin: str, reason: str) -> HTMLResponse:
        return cls._build(target_origin=target_origin, succeeded=False, reason=reason)

    @classmethod
    def _build(
        cls, *, target_origin: str, succeeded: bool, reason: str | None
    ) -> HTMLResponse:
        payload: dict[str, str] = {
            "type": _MESSAGE_TYPE,
            "status": "success" if succeeded else "error",
        }
        if reason is not None:
            payload["reason"] = reason

        payload_js = json.dumps(payload)
        target_origin_js = json.dumps(target_origin)
        post_message = f"window.opener.postMessage({payload_js}, {target_origin_js});"
        return HTMLResponse(
            content=f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Google sign-in</title></head>
<body>
<script>
  (function () {{
    if (window.opener) {{
      try {{ {post_message} }} catch (e) {{}}
    }}
    window.close();
  }})();
</script>
</body>
</html>"""
        )
