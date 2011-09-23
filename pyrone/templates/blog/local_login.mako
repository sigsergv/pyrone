<%inherit file="/blog/base.mako"/>

<%def name="title()">${_('Sign in')}</%def>

% if error != '':
<div class="warning">${error}</div>
% endif

<form  action="${url('account_login')}" method="POST">
<div style="width: 300px;">
<dl class="form">
	<dt>${_('Login name')}:</dt>
	<dd><input type="text" name="login" value="${h.get_setting(request, 'pyrone.default.local_login', '')}"/></dd>
	<dt>${_('Password')}:</dt>
	<dd><input type="password" name="password" value="${h.get_setting(request, 'pyrone.default.local_password', '')}"/></dd>
	<dd><input type="submit" value="${_('sign in')}"/></dd>
</dl>
</div>
</form>
