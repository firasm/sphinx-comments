"""Add a hypothes.is overlay to your Sphinx site."""

import os
from docutils import nodes
from yaml import safe_load
from sphinx.util import logging

__version__ = "0.0.1"

logger = logging.getLogger(__name__)


def shp_static_path(app):
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '_static'))
    app.config.html_static_path.append(static_path)


def activate_comments(app, pagename, templatename, context, doctree):
    """Activate commenting on each page."""
    # Grab config instances
    config = app.config.comments_config.copy()
    if not isinstance(config, (dict, type(None))):
        raise ValueError("Comments configuration must be a dictionary.")

    ut_config = config.get("utterances")
    dk_config = config.get("dokieli")
    ht_config = config.get("hypothesis")

    extra_config = {"async": "async"}

    # Hypothesis config
    if ht_config:
        # If hypothesis, we just need to load the js library
        app.add_js_file("https://hypothes.is/embed.js", **extra_config)

    # Dokieli config
    if dk_config:
        app.add_js_file("https://dokie.li/scripts/dokieli.js", **extra_config)
        app.add_css_file("https://dokie.li/media/css/dokieli.css", media="all")

    # utterances config
    if ut_config:
        if "repo" not in ut_config:
            raise ValueError("To use utterances, you must provide a repository.")
        repo = ut_config["repo"]

        if doctree:
            dom = """
                var commentsRunWhenDOMLoaded = cb => {
                if (document.readyState != 'loading') {
                    cb()
                } else if (document.addEventListener) {
                    document.addEventListener('DOMContentLoaded', cb)
                } else {
                    document.attachEvent('onreadystatechange', function() {
                    if (document.readyState == 'complete') cb()
                    })
                }
                }
            """
            issue_term = ut_config.get("issue-term", "pathname")
            theme = ut_config.get("theme", "github-light")
            label = ut_config.get("label", "💬 comment")
            crossorigin = ut_config.get("crossorigin", "anonymous")
            js = f"""
            {dom}
            var addUtterances = () => {{
                var script = document.createElement("script");
                script.type = "text/javascript";
                script.src = "https://utteranc.es/client.js";
                script.async = "async";

                script.setAttribute("repo", "{repo}");
                script.setAttribute("issue-term", "{issue_term}");
                script.setAttribute("theme", "{theme}");
                script.setAttribute("label", "{label}");
                script.setAttribute("crossorigin", "{crossorigin}");

                sections = document.querySelectorAll("div.section");
                section = sections[sections.length-1];
                section.appendChild(script);
            }}
            commentsRunWhenDOMLoaded(addUtterances);
            """
            app.add_js_file(None, body=js)


def setup(app):
    app.add_config_value("comments_config", {}, "html")

    # Add our static path
    app.connect('builder-inited', shp_static_path)
    app.connect('html-page-context', activate_comments)

    return {"version": __version__,
            "parallel_read_safe": True,
            "parallel_write_safe": True}