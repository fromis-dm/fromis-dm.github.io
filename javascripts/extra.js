document.addEventListener("DOMContentLoaded", function () {
});

function openFullscreen(imageElement) {
//    console.log('openFullscreen');
//    console.log(imageElement);
    const fullscreenContainer = document.createElement('div');
    fullscreenContainer.style.position = 'fixed';
    fullscreenContainer.style.top = '0';
    fullscreenContainer.style.left = '0';
    fullscreenContainer.style.width = '100%';
    fullscreenContainer.style.height = '100%';
    fullscreenContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    fullscreenContainer.style.display = 'flex';
    fullscreenContainer.style.justifyContent = 'center';
    fullscreenContainer.style.alignItems = 'center';
    fullscreenContainer.style.zIndex = '1000';

    const fullscreenImage = document.createElement('img');
    fullscreenImage.src = imageElement.src.replace('?type=e1920', '');
    fullscreenImage.style.maxWidth = '100%';
    fullscreenImage.style.maxHeight = '100%';

    fullscreenContainer.appendChild(fullscreenImage);
    document.body.appendChild(fullscreenContainer);

    fullscreenContainer.onclick = () => {
        document.body.removeChild(fullscreenContainer);
    };
}