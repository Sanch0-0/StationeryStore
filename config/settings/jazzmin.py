logo = ('logo/logo.jpg')

JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Stationery Store",
    "show_language_picker": True,

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Admin Panel",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Stationery Store",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": logo,
    
    # Add these logo size controls:
    "site_logo_classes": "img-fluid",  # Keep this for responsiveness
    "login_logo_classes": "img-fluid",  # For login page specifically

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": logo,

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": None,

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-fluid",

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": logo,

    # Welcome text on the login screen
    "welcome_sign": "Welcome to the Admin panel!",

    # Copyright on the footer
    "copyright": "Stationery Store",

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": "avatar",

    # Links to put along the top menu
    "topmenu_links": [
        {"name": "To the website", "url": "/", "permissions": ["auth.view_user"]},
        # {"name": "Russian", "url": "/admin/?language=ru", "new_window": False},
        # {"name": "English", "url": "/admin/?language=en", "new_window": False},
    ],

    #############
    # User Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": [""],

    # for the full list of 5.13.0 free icon classes
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },

    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    # Use modals instead of popups
    "related_modal_active": False,

    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": "css/admin_custom.css",
    "custom_js": None,

    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,

    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,

    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tab"},
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": "navbar-indigo",
    "accent": "accent-success",
    "navbar": "navbar-indigo navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": True,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-light-indigo",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "litera",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-sm btn-outline-primary",
        "secondary": "btn-sm btn-outline-secondary",
        "info": "btn-sm btn-info",
        "warning": "btn-sm btn-warning",
        "danger": "btn-sm btn-danger",
        "success": "btn-sm btn-outline-success"
    },
    "actions_sticky_top": True
}