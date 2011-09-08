<%
    authenticated = user.kind != 'anonymous'
    
    lang = h.lang.lang(request)
%>

<div class="widget">
%if not authenticated:
<div>${_('<strong>Sign in</strong> using')|n} 
  <a href="#" onclick="Pyrone.account.loginTwitter('${url('account_twitter_init')}');\
  return false;">twitter</a>
  <a href="#">google</a>
  <a href="${url('account_login_form')}">local</a>
  </div>
%else:
    <div>${_('You are logged in.')}</div>
    <div><a href="${url('account_my_profile')}">${_('My profile page')}</a></div>
    <div><a href="${url('account_my_subscriptions')}">${_('My subscriptions')}</a></div>
    <div><a href="#" onclick="Pyrone.account.logout('${url('account_logout', t=h.auth.get_logout_token(request))}'); return false;">${_('Logout')}</a></div>
%endif

## languages
<div class="lang-selector">
% for lang_code in h.lang.supported_langs():
  % if lang == lang_code:
    <span class="active">${h.lang.lang_title(lang_code)}</span>
  % else:
    <span><a href="#" onclick="Pyrone.lang.set('${lang_code}'); return false;">${h.lang.lang_title(lang_code)}</a></span>
  % endif
% endfor
</div>
</div>