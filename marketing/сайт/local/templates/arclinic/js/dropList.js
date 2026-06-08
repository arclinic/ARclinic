function dropList() {
  const nav = document.querySelector('.menu');
  const menuParent = nav.querySelector('.menu__item--parent');
  const servicesParent = nav.querySelectorAll('.menu__item--parent > a');
  const list = menuParent.querySelector('.menu__list--inserted');

  const linkActive = list.querySelector('.menu__link--inserted_active');
  if (linkActive) {
    list.style.maxHeight = list.scrollHeight + 'px';
    // if (servicesParent) {
    //   servicesParent.classList.add('link_active');
    // }
  }

  if (servicesParent) {
    servicesParent.forEach((el) => {
      el.addEventListener('click', (e) => {
        let elSibling = el.parentNode.querySelector('.menu__list--inserted');
        if (window.innerWidth <= 1170) {
          e.preventDefault();
          el.classList.toggle('link_active');
          if (elSibling.style.maxHeight) {
            elSibling.style.maxHeight = null;
          } else {
            elSibling.style.maxHeight = elSibling.scrollHeight + 'px';
          }
        }
      });
    });
  }
}
dropList();
function cookie  () {
   function recordCookieValue(cookieName, value) {
    document.cookie = `${cookieName}=${value}; max-age= 15768000;  path=/`;
   }
    function getCookieValue(cookieName) {
    const cookieString = document.cookie;
    const cookieArray = cookieString.split(';');
    for (let i = 0; i < cookieArray.length; i++) {
      let cookie = cookieArray[i];
      while (cookie.charAt(0) == ' ') {
        cookie = cookie.substring(1);
      }
      if (cookie.indexOf(cookieName + '=') == 0) {
        return cookie.substring(cookieName.length + 1, cookie.length);
      }
    }
  
    return undefined;
  }
  const cookie = document.querySelector('.cookie-alert');
  if (!getCookieValue('cookie')) {
    cookie.classList.add('open')
  }
if (cookie) {
  const close = cookie.querySelector('.btn');
  close.addEventListener('click', () => {
    recordCookieValue('cookie', 'close');
    cookie.classList.remove('open');
  });
}
}
cookie()
