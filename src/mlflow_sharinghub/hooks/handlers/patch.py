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
from mlflow_sharinghub.utils.http import clean_url

_INJECT_JS = """
function isIframe () {{
    try {{
        return window.self !== window.top;
    }} catch (e) {{
        return true;
    }}
}}

function waitForElm(selector) {{
    return new Promise(resolve => {{
        if (document.querySelector(selector)) {{
            return resolve(document.querySelector(selector));
        }}
        const observer = new MutationObserver(mutations => {{
            if (document.querySelector(selector)) {{
                observer.disconnect();
                resolve(document.querySelector(selector));
            }}
        }});
        observer.observe(document.body, {{
            childList: true,
            subtree: true
        }});
    }});
}}

waitForElm('header').then((header) => {{
    const headerLeftLinks = header.children[1];
    const headerRightLinks = header.children[header.children.length - 1];

    const labelStyle = "transform:translateY(2px);"
    const btnStyle = "font-size:16px;transform:translateY(-8px);";
    const tagStyle = "font-size:12px;height:23px;" +
                     "padding-right:5px;padding-left:5px;" +
                     "transform:translateY(1px);";

    const themeSpan = headerRightLinks.children[0];
    const themeBtn = themeSpan.children[0];
    themeSpan.hidden = true;
    if (themeBtn.ariaChecked == "true") {{
        themeBtn.click();
    }}

    if (!isIframe()) {{
        const projectPath = "{project_path}";
        if (!!projectPath.length) {{
            const projectLink = document.createElement("a");
            projectLink.href = "{project_view}";
            projectLink.target = "_blank";
            projectLink.innerText = projectPath;
            projectLink.className = "du-bois-light-btn du-bois-light-btn-primary";
            projectLink.style = btnStyle;
            headerLeftLinks.appendChild(projectLink);
        }}

        const homeHref = "{home_href}";
        if (!!homeHref.length) {{
            const homeLink = document.createElement("a");
            homeLink.href = homeHref;
            homeLink.innerText = "Home";
            homeLink.className = "du-bois-light-btn du-bois-light-btn-primary";
            homeLink.style = btnStyle;
            headerRightLinks.appendChild(homeLink);
        }} else {{
            const readOnlyTag = document.createElement("span");
            readOnlyTag.className = "du-bois-light-btn du-bois-light-btn-danger";
            readOnlyTag.style = tagStyle;
            readOnlyTag.innerText = "read-only";
            headerLeftLinks.appendChild(readOnlyTag);
        }}

        const logoutHref = "{logout_href}";
        if (!!logoutHref.length) {{
            const logoutLink = document.createElement("a");
            logoutLink.href = logoutHref;
            logoutLink.innerText = "Logout";
            logoutLink.className = "du-bois-light-btn du-bois-light-btn-danger";
            logoutLink.style = btnStyle;
            headerRightLinks.appendChild(logoutLink);
        }}
    }} else {{
        const refreshLink = document.createElement("a");
        refreshLink.href = "";
        refreshLink.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="2em" height="20px" fill="none" viewBox="0 0 16 16" aria-hidden="true" focusable="false" class=""><path fill="currentColor" d="M8 2.5a5.48 5.48 0 0 1 3.817 1.54l.009.009.5.451H11V6h4V2h-1.5v1.539l-.651-.588A7 7 0 0 0 1 8h1.5A5.5 5.5 0 0 1 8 2.5ZM1 10h4v1.5H3.674l.5.451.01.01A5.5 5.5 0 0 0 13.5 8h1.499a7 7 0 0 1-11.849 5.048L2.5 12.46V14H1v-4Z"></path></svg>`;
        refreshLink.style = labelStyle;
        headerRightLinks.appendChild(refreshLink);
    }}
}});
"""  # noqa: E501


def alter_main_js(resp: Response) -> None:
    """Fix the main js file of the built frontend."""
    project_path = get_project_path()
    if project_path and AppConfig.GITLAB_URL:
        project_view = f"{clean_url(AppConfig.GITLAB_URL)}/{project_path}"
    elif project_path and AppConfig.SHARINGHUB_URL:
        base_url = clean_url(AppConfig.SHARINGHUB_URL)
        collection = AppConfig.SHARINGHUB_STAC_COLLECTION
        project_view = (
            f"{base_url}/ui/#/api/stac/collections/"
            f"{collection}/items/{project_path}"
        )
    else:
        project_view = ""
    inject_js = ";\n" + _INJECT_JS.format(
        home_href=url_for("home", _root=True) if project_path else "",
        logout_href=url_for("auth.logout") if AppConfig.GITLAB_URL else "",
        project_path=project_path if project_path else "",
        project_view=project_view,
    )

    resp.direct_passthrough = False
    resp.set_data(resp.get_data() + inject_js.encode())
