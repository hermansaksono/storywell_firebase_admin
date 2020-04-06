from admin import constants


def get_nav(active="none") -> dict:
    activated_nav = constants.nav_default.copy()

    if active in constants.nav_default:
        for key, value in activated_nav.items():
            value["is_active"] = False
        activated_nav[active]["is_active"] = True
        return activated_nav
    else:
        return activated_nav
