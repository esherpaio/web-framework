from web.packer.base import CssBundle, JsBundle, Packer


def generate_admin_static() -> None:
    js_dir = "/home/stan/code/web-framework/web/blueprint/admin/static/js"
    css_dir = "/home/stan/code/web-framework/web/blueprint/admin/static/css"
    Packer().pack(JsBundle(js_dir), save_cdn=True)
    Packer().pack(CssBundle(css_dir), save_cdn=True)


if __name__ == "__main__":
    generate_admin_static()
