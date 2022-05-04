<%
    authenticated = user is not None and user.kind != 'anonymous'
%>

<div class="widget">
%if not authenticated:
<div></div>
##<div>${_('<strong>Sign in</strong> using')|n} 
##  <a href="#" onclick="Pyrone_account_loginTwitter('${url('account_twitter_init')}');\
##  return false;">twitter</a>
##  <!--<a href="#">google</a>-->
##  <a href="${url('account_login')}">local</a>
##  </div>
%else:
    <div>${_('You are logged in.')}</div>
    <div><a href="${url('account_my_profile')}">${_('My profile page')}</a></div>
    <!--<div><a href="${url('account_my_subscriptions')}">${_('My subscriptions')}</a></div>-->
    <div><a href="#" onclick="Pyrone_account_logout('${url('account_logout', t=h.get_logout_token(request))}'); return false;">${_('Logout')}</a></div>
%endif

</div>
