from web.packer.base import CssPacker, JsPacker, Packer


def generate_admin_static() -> None:
    js_dir = "/Users/stan/code/web-framework/web/blueprint/admin/static/js"
    css_dir = "/Users/stan/code/web-framework/web/blueprint/admin/static/css"
    Packer().pack(JsPacker([js_dir]), save_cdn=True)
    Packer().pack(CssPacker([css_dir]), save_cdn=True)


if __name__ == "__main__":
    generate_admin_static()
