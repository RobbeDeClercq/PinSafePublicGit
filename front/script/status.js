// const IP = '192.168.0.233:5000';
const IP = 'robbedc:5000';
const socket = io.connect(IP);


let element, img;

const showPir = function(jsonObject) {
  let datum = new Date(jsonObject[0]['DatumTijd']);
  
  document.querySelector('.c-beweging p').innerHTML = `
                                                    ${datum.getDate()}/${datum.getMonth()+1}/${datum.getFullYear()} 
                                                    &nbsp; ${datum.getUTCHours()} : ${datum.getMinutes()}`;
};

const showHall = function(jsonObject) {
  let datum = new Date(jsonObject[0]['DatumTijd']);
  
  document.querySelector('.statusHall').innerHTML = `De laatste toestandsverandering van de deur gebeurde om: <strong>
                                                    ${datum.getDate()}/${datum.getMonth()+1}/${datum.getFullYear()} 
                                                    &nbsp; ${datum.getUTCHours()} : ${datum.getMinutes()} : ${datum.getSeconds()}</strong>`;
};

socket.on('hall_magnet', function(status){
  if(status.status == 1){
    element.className = 'c-open';
    element.innerHTML = 'Open';
    img.className = 'c-lock__img--open';

  }else{
    element.className = 'c-closed';
    element.innerHTML = 'Gesloten';
    img.className = 'c-lock__img--closed';
    if(document.querySelector('.c-lock__img--closed')){
        document.querySelector('.c-lock__img--closed').addEventListener('click', function(){
            element.className = 'c-open';
            element.innerHTML = 'Open';
            img.className = 'c-lock__img--open';
            socket.emit("open_lock");
          });
    }
  }
});

socket.on('connected',function(){
  console.log('verbinding geslaagd');
});

//#region ***********  INIT / DOMContentLoaded ***********
const init = function() {
  handleData('http://' + IP + '/pir-sensor', showPir, "GET");
  let knoplock = document.querySelector('.c-lock__img--closed');
  element = document.querySelector('.c-status__text span');
  img = document.querySelector('.c-lock span');
  if(knoplock){
      knoplock.addEventListener('click', function(){
      element.className = 'c-open';
      element.innerHTML = 'Open';
      img.className = 'c-lock__img--open';
    });
  }
  socket.emit("hall_control");
};

document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM geladen');
  init();
});
//#endregion