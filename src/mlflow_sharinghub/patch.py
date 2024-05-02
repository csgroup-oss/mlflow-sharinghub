"""Patch module."""

from flask import Response

from mlflow_sharinghub._internal.server import url_for

_INJECT_JS = """
window.onload = () => {{
    const header_links = document.getElementsByClassName("header-links")[0];
    const github_link = header_links.children[1];
    const new_link = github_link.cloneNode();
    new_link.href = "{auth_href}";
    new_link.innerHTML = '<div style="color:#e7f1fb;"><span>SharingHub</span></div>';
    header_links.insertBefore(new_link, github_link);
}};
"""


def alter_main_js(resp: Response) -> None:
    """Fix the main js file of the built frontend."""
    inject_js = ";\n" + _INJECT_JS.format(auth_href=url_for("auth.index"))

    resp.direct_passthrough = False
    resp.set_data(resp.get_data() + inject_js.encode())
