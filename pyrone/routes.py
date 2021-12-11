from pyramid.httpexceptions import HTTPFound


def add_route(config, **r):
    """Adds route with trailing slashes if requested
    """
    is_slashed = '_slashed' in r

    rname = r['name']

    if is_slashed:
        del r['_slashed']
        r['name'] = rname + '_slashed-auto'
        pattern = r['pattern']
        r['pattern'] = pattern + '/'
        config.add_route(**r)

        config.add_view(lambda request: HTTPFound(request.route_url(rname, _query=request.GET, **request.matchdict)),
            route_name=rname + '_slashed-auto')
        r['pattern'] = pattern

    r['name'] = rname
    config.add_route(**r)


def includeme(config):
    routes = [
        {'name': 'static_favicon_png', 'pattern': '/favicon.png'},
        {'name': 'static_favicon_ico', 'pattern': '/favicon.ico'},
        {'name': 'blog_latest', 'pattern': '/'},
        {'name': 'blog_latest_rss', 'pattern': '/rss/latest'},
        {'name': 'blog_tag_articles', 'pattern': '/tag/{tag}', '_slashed': True},
        {'name': 'blog_write_article', 'pattern': '/write'},
        {'name': 'blog_go_article', 'pattern': '/article/{article_id:\d+}'},
        {'name': 'blog_view_article', 'pattern': '/{shortcut_date:\d\d\d\d/\d\d/\d\d}/{shortcut}', '_slashed': True},
        {'name': 'blog_view_moderation_queue', 'pattern': '/comments/moderation'},
        {'name': 'blog_edit_article_ajax', 'pattern': '/article/{article_id:\d+}/edit/ajax'},
        {'name': 'blog_edit_article', 'pattern': '/article/{article_id:\d+}/edit'},
        {'name': 'blog_preview_article', 'pattern': '/preview/article'},
        {'name': 'blog_article_delete_ajax', 'pattern': '/article/{article_id:\d+}/delete/ajax'},
        {'name': 'blog_edit_comment_ajax', 'pattern': '/comment/{comment_id:\d+}/edit/ajax'},
        {'name': 'blog_approve_comment_ajax', 'pattern': '/comment/{comment_id:\d+}/approve/ajax'},
        {'name': 'blog_delete_comment_ajax', 'pattern': '/comment/{comment_id:\d+}/delete/ajax'},
        {'name': 'blog_edit_comment_fetch_ajax', 'pattern': '/comment/{comment_id:\d+}/fetch/ajax'},
        {'name': 'blog_add_article_comment', 'pattern': '/article/{article_id:\d+}/comment'},
        {'name': 'blog_add_article_comment_ajax', 'pattern': '/article/{article_id:\d+}/comment/ajax'},

        {'name': 'account_my_profile', 'pattern': '/me'},
        {'name': 'account_save_my_profile_ajax', 'pattern': '/me/save/ajax'},
        {'name': 'account_login', 'pattern': '/login'},
        {'name': 'account_logout', 'pattern': '/logout'},
        {'name': 'account_verify_email', 'pattern': '/verify-email'},
        {'name': 'account_twitter_init', 'pattern': '/login/twitter/init'},
        {'name': 'account_twitter_finish', 'pattern': '/login/twitter/finish'},
        {'name': 'account_my_subscriptions', 'pattern': '/me/subscriptions'},

        {'name': 'blog_download_file', 'pattern': '/files/f/{filename}'},
        {'name': 'blog_download_file_preview', 'pattern': '/files/p/{filename}'},

        {'name': 'admin_settings', 'pattern': '/admin/settings'},
        {'name': 'admin_settings_save_ajax', 'pattern': '/admin/settings/save/ajax'},
        {'name': 'admin_settings_widget_pages', 'pattern': '/admin/settings/widget/pages'},
        {'name': 'admin_settings_widget_pages_save_ajax', 'pattern': '/admin/settings/widget/pages/save/ajax'},
        {'name': 'admin_list_files', 'pattern': '/admin/files'},
        {'name': 'admin_upload_file', 'pattern': '/admin/file/upload'},
        {'name': 'admin_upload_file_check_ajax', 'pattern': '/admin/file/upload/check'},
        {'name': 'admin_edit_file_props', 'pattern': '/admin/file/{file_id:\d+}/edit'},
        {'name': 'admin_edit_file_props_check_ajax', 'pattern': '/admin/file/{file_id:\d+}/edit/check'},
        {'name': 'admin_delete_files_ajax', 'pattern': '/admin/files/delete/ajax'},
        {'name': 'admin_list_accounts', 'pattern': '/admin/accounts'},
        {'name': 'admin_list_visitors_emails', 'pattern': '/admin/visitors-emails'},
        {'name': 'admin_visitor_email_edit_ajax', 'pattern': '/admin/visitor-email/edit/ajax'},
        {'name': 'admin_visitors_emails_delete_ajax', 'pattern': '/admin/visitors-emails/delete/ajax'},
        {'name': 'admin_delete_accounts_ajax', 'pattern': '/admin/accounts/delete/ajax'},
        {'name': 'admin_list_backups', 'pattern': '/admin/backups'},
        {'name': 'admin_upload_backup', 'pattern': '/admin/backups/upload'},
        {'name': 'admin_delete_backups_ajax', 'pattern': '/admin/backups/delete/ajax'},
        {'name': 'admin_restore_backup', 'pattern': '/admin/backup/{backup_id}/restore'},
        {'name': 'admin_download_backup', 'pattern': '/admin/backup/{backup_id}/download'},
        {'name': 'admin_backup_now', 'pattern': '/admin/backup/now'}
    ]
    for r in routes:
        add_route(config, **r)

    config.add_static_view('static', 'pyrone:static')
