// modals
var $modals = document.querySelectorAll(".modal__overflow");
var $page = document.querySelector("html");
var $container = document.querySelector(".container");

function modalShow(active, modal) {
  if (modal) {
    active ? modal.classList.add("modal__overflow--active") : modal.classList.remove("modal__overflow--active");
    active ? $page.style.overflow = "hidden" : $page.style.overflow = "visible";
    active ? $container.classList.add("container--blur") : $container.classList.remove("container--blur");
  }
  else {
    for (var i = 0; i < $modals.length; i++) {
      modalShow(active, $modals[i]);
    }
  }
}

window.addEventListener("click", function (e) {
  modalShow(false);
});

document.querySelectorAll(".modal__close").forEach(function (elem) {
  elem.addEventListener("click", function (e) {
    modalShow(false);
  });
});

/*document.querySelectorAll(".btn--record").forEach(function (elem) {
  elem.addEventListener("click", function (e) {
    modalShow(true, document.querySelector(".modal__overflow--record"));
    e.stopPropagation();
  });
});*/

document.querySelectorAll(".btn--ask").forEach(function (elem) {
  elem.addEventListener("click", function (e) {
    modalShow(true, document.querySelector(".modal__overflow--ask"));
    e.stopPropagation();
  });
});

document.querySelectorAll(".btn--work_with_us").forEach(function (elem) {
  elem.addEventListener("click", function (e) {
    modalShow(true, document.querySelector(".modal__overflow--job"));
    e.stopPropagation();
  });
});


document.querySelectorAll(".modal__item").forEach(function (elem) {
  elem.addEventListener("click", function (e) {
    e.stopPropagation();
  });
});
//modals end


//menu open with swipe

// document.addEventListener('touchstart', handleTouchStart, false);
// document.addEventListener('touchmove', handleTouchMove, false);
//
// var xDown = null;
// var yDown = null;
//
// function handleTouchStart(evt) {
//   xDown = evt.touches[0].clientX;
//   yDown = evt.touches[0].clientY;
// }
//
// function handleTouchMove(evt) {
//   if (!xDown || !yDown) {
//     return;
//   }
//   var xUp = evt.touches[0].clientX;
//   var yUp = evt.touches[0].clientY;
//
//   var xDiff = xDown - xUp;
//   var yDiff = yDown - yUp;
//
//   if (Math.abs(xDiff) > Math.abs(yDiff)) {/*most significant*/
//     if (xDiff > 0) {
//       if (document.querySelector(".container").classList.contains("container--active")) {
//         mobileMenu();
//       }
//     } else {
//       if (!document.querySelector(".container").classList.contains("container--active")) {
//         mobileMenu();
//       }
//     }
//   } else {
//     if (yDiff > 0) {
//       /* up swipe */
//     } else {
//       /* down swipe */
//     }
//   }
//   /* reset values */
//   xDown = null;
//   yDown = null;
// }

//menu open with swipe end

