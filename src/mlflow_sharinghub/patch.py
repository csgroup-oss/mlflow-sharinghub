# Copyright 2024, CS GROUP - France, https://www.csgroup.eu/
#
# This file is part of SharingHub project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Patch module."""

from flask import Response

from mlflow_sharinghub._internal.server import get_project_path, url_for

_INJECT_JS = """
window.onload = () => {{
    const headerLinks = document.getElementsByClassName("header-links")[0];
    const githubLink = headerLinks.children[1];

    const divider = document.createElement("div");
    divider.className = githubLink.className;
    divider.style.borderRight = "solid 1px #e7f1fb"
    headerLinks.appendChild(divider);

    const logoutLink = githubLink.cloneNode();
    logoutLink.href = "{logout_href}";
    logoutLink.innerHTML = `<div style="color: #e7f1fb;"><span>Logout</span></div>`;
    headerLinks.appendChild(logoutLink);

    const homeHref = "{home_href}";
    if (!!homeHref.length) {{
        const homeLink = githubLink.cloneNode();
        homeLink.href = homeHref;
        homeLink.innerHTML = `<div style="color: #e7f1fb;"><span>Home</span></div>`;
        headerLinks.appendChild(homeLink);
    }}
}};
"""


def alter_main_js(resp: Response) -> None:
    """Fix the main js file of the built frontend."""
    project_path = get_project_path()
    inject_js = ";\n" + _INJECT_JS.format(
        home_href="/" if project_path else "",
        logout_href=url_for("auth.logout"),
    )

    resp.direct_passthrough = False
    resp.set_data(resp.get_data() + inject_js.encode())
