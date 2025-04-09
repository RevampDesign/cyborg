const trustedDomains = ['notdefined.tech', ]; // Add trusted domains here
const affiliateLinks = ['redbubble.com', 'digitalocean.pxf.io', 'usefathom.com']; // Add known affiliate domains here

document.querySelectorAll('a').forEach(link => {
    const linkHostname = link.hostname.replace(/^www\./, ''); // Normalize by removing 'www.'
    const isExternal = linkHostname !== location.hostname.replace(/^www\./, '');
    const isMailto = link.href.startsWith('mailto:');
    const isJavascript = link.href.startsWith('javascript:');
    const isEmptyHref = link.href.trim() === '';
    const isTrustedDomain = trustedDomains.includes(linkHostname);
    const isAffiliate = affiliateLinks.includes(linkHostname);

    if (isExternal && !isMailto && !isJavascript && !isEmptyHref) {
        link.setAttribute('target', '_blank');

        let relValue = link.getAttribute('rel') || '';

        if (!relValue.includes('noopener')) relValue += ' noopener';
        if (!relValue.includes('noreferrer')) relValue += ' noreferrer';

        if (isAffiliate) {
            // If it's an affiliate link, apply "sponsored"
            if (!relValue.includes('sponsored')) relValue += ' sponsored';
        } else if (!isTrustedDomain) {
            // If it's not trusted, apply "nofollow"
            if (!relValue.includes('nofollow')) relValue += ' nofollow';
        }

        link.setAttribute('rel', relValue.trim());
    }
});
