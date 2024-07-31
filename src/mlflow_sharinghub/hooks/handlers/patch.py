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
from mlflow_sharinghub.config import AppConfig

_INJECT_JS = """
window.onload = () => {{
    const header = document.getElementsByTagName("header")[0];
    const headerLinks = header.children[header.children.length - 1];
    const themeSpan = headerLinks.children[0];
    const themeBtn = themeSpan.children[0];
    const githubLink = headerLinks.children[1];

    themeSpan.hidden = true;
    if (themeBtn.ariaChecked == "true") {{
        themeBtn.click();
    }}

    const divider = document.createElement("div");
    divider.className = githubLink.className;
    divider.style.borderRight = "solid 1px #e7f1fb";
    divider.style.marginBottom = "15px";

    const logoutHref = "{logout_href}"
    if (!!logoutHref.length) {{
        const logoutLink = githubLink.cloneNode();
        logoutLink.href = logoutHref;
        logoutLink.innerText = "Logout";
        headerLinks.appendChild(logoutLink);
        if (divider.parentElement == null) {{
            headerLinks.insertBefore(divider, logoutLink);
        }}
    }}

    const homeHref = "{home_href}";
    if (!!homeHref.length) {{
        const homeLink = githubLink.cloneNode();
        homeLink.href = homeHref;
        homeLink.innerText = "Home";
        headerLinks.appendChild(homeLink);
        if (divider.parentElement == null) {{
            headerLinks.insertBefore(divider, homeLink);
        }}
    }}
}};
"""


def alter_main_js(resp: Response) -> None:
    """Fix the main js file of the built frontend."""
    project_path = get_project_path()
    inject_js = ";\n" + _INJECT_JS.format(
        home_href="/" if project_path else "",
        logout_href=url_for("auth.logout") if AppConfig.GITLAB_URL else "",
    )

    resp.direct_passthrough = False
    resp.set_data(resp.get_data() + inject_js.encode())
