document.querySelectorAll('a').forEach(link => {
    if (
        link.hostname !== location.hostname && // External links
        !link.href.startsWith('mailto:') &&  // Ignore mailto links
        !link.href.startsWith('javascript:') && // Ignore javascript links
        link.getAttribute('rel') !== 'sponsored' && // Ignore sponsored links
        link.href.trim() !== '' && // Ignore empty hrefs
        !link.hasAttribute('rel') // Only modify if rel isn't already set
    ) {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener');
    }
});
