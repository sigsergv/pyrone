## vim: shiftwidth=2 tabstop=2
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.1/jquery.min.js"></script>
  <script language="javascript" src="/static/lang/${h.lang.lang(request)}.js"></script>
  <script language="javascript" src="/static/scripts/blog.js"></script>
  <script language="javascript" src="/static/scripts/admin.js"></script>
  <link rel="icon" type="image/png" href="/favicon.png"/>
  <link rel="stylesheet" type="text/css" href="${h.get_current_theme_css()}"/>
  <link rel="stylesheet" type="text/css" href="/static/font-awesome/css/font-awesome.min.css"/>
  <title>${self.title()} — ${h.get_config('site_title')} — ${_('administration')}</title>
</head>
<body>
<div id="topbar-admin" class="admin"><div class="title"><a href="/">${h.get_config('site_title')}</a> / ${_('administration')}</div><div class="version">${_('pyrone version: {0}').format(h.PYRONE_VERSION)}</div></div>
  <div id="contentbar">
    <div id="content">
    ${next.body()}
    </div>
    <div id="bottombar"><div class="title">${h.get_config('site_copyright')} | <a href="https://github.com/sigsergv/pyrone">${_('Powered by Pyrone')}</a></div>
    </div>
  </div>

  <div id="sidebar">
    <%include file="/widgets/account.mako"/>
    <%include file="/widgets/actions.mako"/>
  </div>
</body>
</html>
