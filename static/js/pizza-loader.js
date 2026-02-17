const kawalki_pizzy = document.querySelectorAll('.ekran_ladowania .kawalek_pizzy img');
let indeks = 0;
let wypelnianie = true;

const interval_id = setInterval(() => {
  const ekran_ladowania = document.querySelector('.ekran_ladowania');

  if (!ekran_ladowania) {
    clearInterval(interval_id);
    return;
  }

  if (wypelnianie) {
    kawalki_pizzy[indeks].src = 'images/pizza/pizza_pionowo_mix.png';
    indeks++;
    if (indeks >= kawalki_pizzy.length) {
      wypelnianie = false;
      indeks = 0;
    }
  } else {
    kawalki_pizzy[indeks].src = 'images/pizza/pizza_pionowo_pusta.png';
    indeks++;
    if (indeks >= kawalki_pizzy.length) {
      wypelnianie = true;
      indeks = 0;
    }
  }
}, 250);
