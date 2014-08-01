Subject: ${_('EMAIL# SUBJECT SOMEONE ANSWERED TO YOUR COMMENT').format(article_title=article_title, comment_author_name=comment_author_name, comment_author_email=comment_author_email, site_title=site_title)}
<div style="font-family: sans-serif;">
<h4>${_(site_title)}</h4>

<div style="margin-bottom: 10px;">${_('EMAIL# USER ANSWERED TO YOUR COMMENT FOR THE ARTICLE').format(article_title=article_title, article_url=article_url)|n}</div>

<div style="margin-bottom: 10px;">${_('EMAIL# VISITOR ON DATE WROTE THE FOLLOWING').format(comment_author_name=comment_author_name, comment_author_email=comment_author_email, comment_date=comment_date)|n}</div>

<blockquote style="border: 4px solid #989; border-style: none none none solid; padding: 4px; background-color: #eee; white-space: pre;">${comment_text}</blockquote>

<div>${_('EMAIL# DIRECT LINK TO COMMENT').format(comment_url=comment_url)|n}</div>

</div>