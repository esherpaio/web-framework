from web.packer.packer import CssBundle, JsBundle, Packer


def generate_admin_static() -> None:
    Packer().pack(
        JsBundle(
            "/home/stan/code/web-framework/web/blueprint/admin/static/js",
            subdirs=True,
        ),
        save_cdn=True,
    )
    Packer().pack(
        CssBundle(
            "/home/stan/code/web-framework/web/blueprint/admin/static/css",
            subdirs=False,
        ),
        save_cdn=True,
    )


if __name__ == "__main__":
    generate_admin_static()
