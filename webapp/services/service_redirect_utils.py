from urllib.parse import urlparse, urljoin
from flask import request, url_for, redirect


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='marketplace.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if target.endswith('users/login_register'):
            return redirect(url_for(default))
        if is_safe_url(target):
            return redirect(target)

    return redirect(url_for(default, **kwargs))
