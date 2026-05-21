# hub/templates — Shared File Templates

Place template files here that will be rendered and copied to multiple CLI targets.

Templates support `{PLACEHOLDER}` tokens that are substituted during fanout.
The renderer is `.unicli-hub/scripts/render_templates.py`.

Run `./sync.sh --fix` to fanout all templates.
