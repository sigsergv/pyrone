Subject: ${_('EMAIL# SUBJECT PLEASE VERIFY YOUR EMAIL ADDRESS FOR THE SITE').format(site_title=site_title)}
<div style="font-family: sans-serif;">
<h4>${_(site_title)}</h4>

<div style="margin-bottom: 10px;">${_('EMAIL# TO RECEIVE NOTIFICATIONS FROM SITE YOU MUST CONFIRM THIS ADDRESS').format(site_title=site_title, email=email)|n}</div>

<div style="margin-bottom: 10px;"><a href="${verify_url}">${_('EMAIL# PLEASE CLICK HERE TO VERIFY ADDRESS')}</a></div>
</div>