// Function to set up common head elements
export function setupHeader(pageTitle) {
    // Get the head element
    const head = document.head;
    
    // Set charset if not present
    if (!document.charset) {
        const charset = document.createElement('meta');
        charset.setAttribute('charset', 'UTF-8');
        head.appendChild(charset);
    }

    // Set favicon
    let favicon = head.querySelector('link[rel="icon"]');
    if (!favicon) {
        favicon = document.createElement('link');
        favicon.setAttribute('rel', 'icon');
        favicon.setAttribute('type', 'image/png');
        favicon.setAttribute('href', '../../public/favicon.png');
        head.appendChild(favicon);
    }

    // Set title
    document.title = pageTitle ? `AnchorChat${pageTitle !== 'AnchorChat' ? ' - ' + pageTitle : ''}` : 'AnchorChat';

    // Add stylesheet if not present
    let stylesheet = head.querySelector('link[href="style.css"]');
    if (!stylesheet) {
        stylesheet = document.createElement('link');
        stylesheet.setAttribute('rel', 'stylesheet');
        stylesheet.setAttribute('href', 'style.css');
        head.appendChild(stylesheet);
    }
} 