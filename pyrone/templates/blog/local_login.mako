<%inherit file="/blog/base.mako"/>

<%def name="title()">${_('Sign in')}</%def>

% if c.error != '':
<div class="warning">${c.error}</div>
% endif

<form  action="${h.url(controller='account', action='login')}" method="POST">
<div style="width: 300px;">
<dl class="form">
	<dt>${_('Login name')}:</dt>
	<dd><input type="text" name="login" value="admin"/></dd>
	<dt>${_('Password')}:</dt>
	<dd><input type="password" name="password" value="setup"/></dd>
	<dd><input type="submit" value="${_('sign in')}"/></dd>
</dl>
</div>
</form>
