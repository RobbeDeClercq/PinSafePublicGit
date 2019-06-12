// const IP = '192.168.0.233:5000';
const IP = 'robbedc:5000';
const socket = io.connect(IP);

let actiefDOM, beschikDOM;

const refresh = function(data){
    location.reload();
};

const showActief = function(jsonData) {
    if(jsonData.length > 0){
        let codesHTML = ''
        for(let code of jsonData){
            codesHTML += `<div class="c-actief__item">
                                <span class="c-actief__pin">${code.Code}</span>
                                <span class="c-img__delet" id="code${code.Code}" value="${code.Code}"></span>
                        </div>`;
        }
        actiefDOM.innerHTML = codesHTML;
        document.querySelector('.c-actief p').innerHTML = "";
        for(let code of jsonData){
            document.querySelector(`#code${code.Code}`).addEventListener('click', function(){
                let result = confirm(`Wilt u zeker de code ${code.Code} deactiveren`);
                if(result == true){
                    handleData('http://' + IP + `/pincodes_change/${code.Code}/0`, refresh, "PUT");
                }
            });
        }
    }else{
        actiefDOM.innerHTML = "";
        actiefDOM.style.border = "0px";
    }
    
    

};

const showBesch = function(jsonData) {
    let inputHTML = document.querySelector('.c-input__select');
    let options = '';
    for(let code of jsonData){
        options += `<option value='${code.Code}'>${code.Code}</option>`;
    }
    inputHTML.innerHTML += options;
    showCombo();
};

//#region ***********  INIT / DOMContentLoaded ***********
const init = function() {
  // handleData('http://' + IP + '/hall-sensor',showHall, "GET");
  actiefDOM = document.querySelector('.c-actief__codes');
  beschikDOM = document.querySelector('.c-beschik');
  handleData('http://' + IP + '/pincodes_actief',showActief, "GET");
  handleData('http://' + IP + '/pincodes_beschik',showBesch, "GET");
};

document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM geladen');
  init();
});
//#endregion









const showCombo = function(){
    let x, i, j, selElmnt, a, b, c;
    /*look for any elements with the class "custom-select":*/
    x = document.getElementsByClassName("custom-select");
    for (i = 0; i < x.length; i++) {
    selElmnt = x[i].getElementsByTagName("select")[0];
    /*for each element, create a new DIV that will act as the selected item:*/
    a = document.createElement("DIV");
    a.setAttribute("class", "select-selected");
    a.innerHTML = selElmnt.options[selElmnt.selectedIndex].innerHTML;
    x[i].appendChild(a);
    /*for each element, create a new DIV that will contain the option list:*/
    b = document.createElement("DIV");
    b.setAttribute("class", "select-items select-hide");
    for (j = 1; j < selElmnt.length; j++) {
        /*for each option in the original select element,
        create a new DIV that will act as an option item:*/
        c = document.createElement("DIV");
        c.innerHTML = selElmnt.options[j].innerHTML;
        c.addEventListener("click", function(e) {
            /*when an item is clicked, update the original select box,
            and the selected item:*/
            let y, i, k, s, h;
            s = this.parentNode.parentNode.getElementsByTagName("select")[0];
            h = this.parentNode.previousSibling;
            for (i = 0; i < s.length; i++) {
            if (s.options[i].innerHTML == this.innerHTML) {
                s.selectedIndex = i;
                h.innerHTML = this.innerHTML;
                y = this.parentNode.getElementsByClassName("same-as-selected");
                for (k = 0; k < y.length; k++) {
                y[k].removeAttribute("class");
                }
                this.setAttribute("class", "same-as-selected");
                break;
            }
            }
            h.click();
        });
        b.appendChild(c);
    }
    x[i].appendChild(b);
    a.addEventListener("click", function(e) {
        /*when the select box is clicked, close any other select boxes,
        and open/close the current select box:*/
        e.stopPropagation();
        closeAllSelect(this);
        this.nextSibling.classList.toggle("select-hide");
        this.classList.toggle("select-arrow-active");


    });
    }

    document.querySelector('.c-img__ok').addEventListener('click', function(){
        if(document.querySelector(".select-selected").innerHTML != "Kies pincode:"){
            let code = document.querySelector('.select-selected').innerHTML;
        let result = confirm(`Wilt u zeker de code ${code} activeren`);
        if(result == true){
            handleData('http://' + IP + `/pincodes_change/${code}/1`, refresh, "PUT");
        }
        }
    });
    

    function closeAllSelect(elmnt) {
    /*a function that will close all select boxes in the document,
    except the current select box:*/
    let x, y, i, arrNo = [];
    x = document.getElementsByClassName("select-items");
    y = document.getElementsByClassName("select-selected");
    for (i = 0; i < y.length; i++) {
        if (elmnt == y[i]) {
        arrNo.push(i)
        } else {
        y[i].classList.remove("select-arrow-active");
        }
    }
    for (i = 0; i < x.length; i++) {
        if (arrNo.indexOf(i)) {
        x[i].classList.add("select-hide");
        }
    }
    }
    /*if the user clicks anywhere outside the select box,
    then close all select boxes:*/
    document.addEventListener("click", closeAllSelect);
};