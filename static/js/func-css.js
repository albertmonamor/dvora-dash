function loading(_this){
    _this.children[0].remove();
    cntr = document.createElement("center");
    dv = document.createElement("div");
    dv.className = "loading";
    cntr.append(dv);
    _this.appendChild(cntr);
}


function unloading(_this, text){
    _this.children[0].remove();
    span = document.createElement("span");
    span.innerText = text
    _this.appendChild(span);
}


function showAlert(title, des){
    document.getElementById("modal-show").style.display = "block";
    $("#alert-title").html(title);
    $("#alert-des").html(des);
}

function showModal(_temp){
    document.getElementById("mfull").style.display = "block";
    document.getElementById("mfull-body").innerHTML = _temp;

}
function closeModal(action=null){
    if (action == 1){
        next_level = []
        
    }
    document.getElementById("mfull").style.display = "none";
}

function setLevelText(nl){
    document.getElementById("level").innerText = nl+'/10';
    ShowProgressStatus(parseInt(nl-2));
}
function showNextLevel(_this, nl, force=null, call_java=0){
    if (force){
        if (_this != undefined){_this.parentElement.parentElement.style.display = "none";}
        document.getElementById(nl).style.display = "block";
        setLevelText(nl);
        return  0;
    }
    if (_this != undefined){
        $.ajax({
            url:"/new_lead", 
            type:"POST", 
            data:{"level":nl-1,"value":_this.parentElement.parentElement.children[1].children[0].value},
            success:(res)=>{
                if (!res.success){
                    showAlert(res.title, res.notice)
                }else{
                    _this.parentElement.parentElement.style.display = "none";
                    document.getElementById(nl).style.display = "block";
                    setLevelText(nl)
                }
            }
        })
    }

}

function showPrevLevel(_this, nl, force=null, call_java=0){
    console.log(nl)
    _this.parentElement.parentElement.style.display = 'none';
    document.getElementById(nl).style.display = "block";
    setLevelText(nl);
}
/**
 * 
 * @param {String} word 
 * @returns {null}
 */
function showSupplyBySearch(word){
    /** add box of supply name */
    /** reset */
    element = document.getElementById("list-supply");
    element.innerHTML = "";
    for ([key, value] of Object.entries(supply_json)){
        if (value.name.indexOf(word) > -1 && word.length > 0){
            box = document.createElement("div");
            box.className = "box-supply";
            box.id = value.id;
            price = document.createElement("h1");
            price.textContent = value.price + "₪";
            n_supply = document.createElement('span')
            n_supply.textContent = value.name
            div_btn = document.createElement("div")
            div_btn.className = "box-action"; 
            btnp=document.createElement("button");btnm=document.createElement("button")
            btnp.className="button-dash";btnm.className="button-dash";
            num_supply = document.createElement("span");
            num_supply.textContent = "0";
            btnp.onclick = ()=>{addSupply(div_btn, 1)};
            btnp.innerHTML += '<i class="fa-solid fa-plus"></i>';
            btnp.id = "plus";
            btnm.onclick = ()=>{addSupply(div_btn, 0)};
            btnm.innerHTML += '<i class="fa-solid fa-minus"></i>';
            btnm.id = "minus";
            box.appendChild(price);
            box.appendChild(n_supply)
            div_btn.appendChild(btnp); 
            div_btn.appendChild(num_supply);
            div_btn.appendChild(btnm);
            box.appendChild(div_btn);
            element.appendChild(box);
        }
    }
}

/**
 * 
 * @param {object} _this 
 * @param {Int16Array} operator
 */
function addSupply(_this, operator){
    nums = _this.children[1];
    nadd = parseInt(nums.innerText);
    if (operator){
        nums.innerText = parseInt(nums.innerText)+1;
    }else if (nadd){
        nums.innerText = parseInt(nums.innerText)-1;
    }
    
}

function startAddLead(_this){
    $.ajax({
        url:'/new_lead',
        type: "POST",
        data:{"level":1, 'value':"password:l<I>lP<e*2>P"},
        success:(res)=>{
            if (res.success){
                showNextLevel(_this, "2", force=true);
            }
            else{
                showAlert(res.title, res.notice);
            }
        }
    })
}
function cleanHash () { 
    history.pushState("", document.title, window.location.pathname + window.location.search);
}


function pasteText(element){
    // Copy the text inside the text field
    element = navigator.clipboard.readText();
}
function pasteToInput(_this){
    if (window.isSecureContext){
        pasteText(_this.innerText);
    }
}
/* dashboard */

/**  UI 
 * 
*/
function tabSelected(_this){
    div_exist = document.getElementsByClassName('tab-selected')
    
    if (div_exist.length > 0){
        div_exist[0].parentNode.removeChild(div_exist[0])
    }
    _this.innerHTML += "<div class='tab-selected'></div>";
}

/**
 * requests
 */

/**
 * contain all templates of dashboard that need
 */
const templates         = {}
var supply_json         = []
const supply_seleceted  = {}  
/**
 * 
 * @param {object} _this 
 * @returns null
 */
function getTemplate(_this){

    tmp_num = _this.id
    _parent = document.getElementsByClassName("dash-template")[0]
    tabSelected(_this);
    if (templates[tmp_num] != undefined){
        _parent.innerHTML = templates[tmp_num];
        return 0;
    }
    $.ajax({
        url:"/template/"+_this.id,
        type:"POST",
        success:
            (res) => {
                if (res.success){
                    _parent.innerHTML = res.template
                    templates[tmp_num] =  res.template
                    
                }
                else{
                    showAlert(res.title, res.notice);
                }
            }
        
    })
    
}

function getSubTemplpateDashboard(_this)
{

    $.ajax({
        url:'/template/'+_this.id,
        type:"POST",
        success:(res)=>{
            if (res.success){
                showModal(res.template);
                showNextLevel(undefined, "1", true);
                if (res.supply!=undefined){
                    supply_json = res.supply;
                }
            }

            else{
                showAlert(res.title, res.notice);
            }
        }
    })
    
    
}


/***
 * show alert 
 */


sp_close = document.getElementsByClassName("modal-show-close")[0];
// sp_mfull_close = document.getElementsByClassName("mfull-close")[0];
modal_show = document.getElementById("modal-show")

sp_close.onclick = function() {
    modal_show.style.display = "none";
}
// sp_mfull_close.onclick = function(){}

window.onclick = function(event) {
    if (event.target == modal_show) {
        modal_show.style.display = "none";
}
}