function loading(_this){
    _this.children[0].remove();
    cntr = document.createElement("center");
    dv = document.createElement("div");
    dv.className = "loading";
    cntr.append(dv);
    _this.appendChild(cntr);
}

function loading2(_this){
    lhtml = _this.innerHTML;
    _this.innerHTML = `<i class="fa-solid fa-atom fa-spin"></i>`
}
/**
 * 
 * @param {Element} _this 
 * @param {String} text 
 */
function unloading(_this, text){
    _this.children[0].remove();
    span = document.createElement("span");
    span.innerText = text
    _this.appendChild(span);
}

function cleanHash () { 
    history.pushState("", document.title, window.location.pathname + window.location.search);
}

// MODAL
function showModal(_temp){
    document.getElementById("mfull").style.display = "block";
    document.getElementById("mfull-body").innerHTML = _temp;

}
function closeModal(action=null){
    if (action == 1){
        next_level = []
        
    }
    document.getElementById("model-addlead").style.display = "none";
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
            // box
            box = document.createElement("div");
            box.className = "box-supply";
            box.id = value.id;
            // price
            price = document.createElement("h1");
            price.textContent = value.price + "₪";
            // number of supply
            n_supply = document.createElement('span')
            n_supply.textContent = value.name
            // supply exist on server
            exist_supp = document.createElement("span")
            exist_supp.textContent = "ציוד זמין: " + value.exist;

            div_btn = document.createElement("div")
            div_btn.className = "box-action"; 
            btnp=document.createElement("button");btnm=document.createElement("button")
            btnp.className="button-dash";btnm.className="button-dash";
            num_supply = document.createElement("span");
            num_supply.textContent = value.count;
            btnp.onclick = function(){addSupply(this, 1);}
            btnp.innerHTML += '<i class="fa-solid fa-plus"></i>';
            btnp.id = "plus";

            btnm.onclick = function(){addSupply(this, 0); }
            btnm.innerHTML += '<i class="fa-solid fa-minus"></i>';
            btnm.id = "minus";

            box.appendChild(price);
            box.appendChild(n_supply);
            box.appendChild(exist_supp);
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
    nums = _this.parentElement.children[1];
    nadd = parseInt(nums.textContent);
    supply = supply_json[_this.parentElement.parentElement.id];
    if (operator && nadd >= parseInt(supply["exist"]) ){setTimeout(()=>{_this.classList.remove("rotate")}, 500); _this.classList.add("rotate");return ;}
    if (operator){
        nums.innerText = nadd+1;
        
    }else if (nadd){
        nums.innerText = nadd-1;
    }
    
    supply_json[_this.parentElement.parentElement.id]["count"] = nums.innerText;
    
}
function showSummery(_this, nl){
    showNextLevel(_this,nl, true);
    parent = document.getElementById("summery");
    parent.innerHTML = "";
    //
    for(var i=2;i<10;i++){
        // varable
        _id = "d"+i;
        oper= "";
        text = document.getElementById(_id).value;
        type = document.getElementById(_id).name

        box = document.createElement("div");
        box.classList.add("box-summery");
        if (!text){
            text = "לא צוין"
            box.classList.add("summ-worng")
        }
        else if (_id == "d9" || _id == 'd8'){
            oper = "₪"
        }
        // header
        _head = document.createElement("div");
        _head.classList.add("box-summery-head");
        _title = document.createElement("p");
        _title.textContent = type
        _level = document.createElement("span");
        _level.textContent = (i-1)+" מתוך 8"
        _head.appendChild(_title);
        _head.appendChild(_level);
        box.appendChild(_head)
        // selfbox
       if (_id == "d5"){
            for ([key, value] of Object.entries(supply_json)){
                if (value["count"]> 0){
                    _div_s = document.createElement("div");
                    _div_s.className = "list-summery-supply"
                    _name = document.createElement("span");
                    _name.textContent = value["name"];
                    _count = document.createElement("span");
                    _count.textContent = value["count"];
                    _div_s.appendChild(_name);
                    _div_s.appendChild(_count);
                    box.appendChild(_div_s);
                    
                }
            }
            parent.appendChild(box);
            continue;
       }
       _name = document.createElement("h1");
       _name.textContent = text+oper;
       box.appendChild(_name);
       parent.appendChild(box);
    }
}

/* dashboard */

/**  UI 
 * @param _this {Element}
*/
function tabSelected(_this){
    div_exist = document.getElementsByClassName('tabs-button-selected')
    
    if (div_exist.length > 0){
        div_exist[0].parentNode.removeChild(div_exist[0])
    }
    _this.innerHTML += "<div class='tabs-button-selected'></div>";
}

/**
 * requests
 */

/**
 * contain all templates of dashboard that need
 */
var templates         = {0:{tmp:'', name:''},
                           1:{tmp:'', name:''},
                           2:{tmp:'', name:''},
                           3:{tmp:'', name:''},
                           4:{tmp:'', name:''}}
var supply_json         = {}
var total               = 0
const identify_total    = {}
var search_is_open      = {"client":0, "history":0}
/**
 * 
 * @param {object} _this 
 * @returns null
 */
function show_popup_error(res, _this){
    //$(_this).hide(300);
    var popup = document.getElementById("popup");
    var title = document.getElementById("popup-title");
    var notice = document.getElementById("popup-notice");
    title.innerHTML += res.title;
    notice.innerText = res.notice;
    popup.style.display = "block";
    setTimeout(()=>{popup.style.display = "none";title.innerText="";notice.innerText="";$(_this).show(300);},2000);
}

function show_loading_screen(){
    load = document.createElement("div")
    load.classList.add("load-screen")
    load.id = "load-screen"
    load.innerHTML = `<i class="fa-solid fa-tower-broadcast fa-bounce"></i>`
    document.body.appendChild(load)

}
function close_loading_screen(){
    document.getElementById("load-screen").remove();
}

function getTemplate(_this, _id, reget=0){
    tmp_num = _id;    
    _parent = document.getElementsByClassName("dashboard-template")[0];

    tabSelected(_this);
    setLastTemplate(_id);

    if (templates[tmp_num].tmp !='' && !reget){
        _parent.innerHTML = templates[tmp_num].tmp;
        document.getElementById("tab-name").innerText = templates[tmp_num].name;
        if (search_is_open.client && _id == 0){
            showSearchLeads(document.getElementById('opensearch'))
        }
        if (search_is_open.history && _id == 2){
            showSearchHistory(document.getElementById("opensearch"))
            
        }
        return 0;
    }
    show_loading_screen()
    $.ajax({
        url: "/template/" + _this.id,
        type: "POST",
        success: (res) => {
          if (res.success) {
            _parent.innerHTML = res.template;
            document.getElementById("tab-name").innerText = res.name;
            templates[tmp_num] = { "tmp": res.template, "name": res.name };
          } else {
            show_popup_error(res, _this);
          }
          close_loading_screen();
        },
        error: (xhr, status, error) => {
          close_loading_screen();
          show_popup_error({ "title": "שגיאת רשת", "notice": "וודא שאתה מחובר" });
        }
      });
    
}

/**
 * 
 * @param {String} _id 
 * @returns {Boolean}
 */
function setLastTemplate(_id){
    localStorage.setItem("l_template", _id)
    return true;
}
/**
 * 
 * @returns {String}
 */
function getLastTemplate(){
    t = localStorage.getItem("l_template")
    if (t == undefined){
        return '0' 
    }
    return t
}
function createTableEquipmentSelected(){
    const parent = document.getElementById("tableequipment");
    const tbody = parent.children[1];
    tmp_total_money_equip = 0

    equipment_selected = []
    for ([key, values] of Object.entries(supply_json)){ 
        if (!values.count){continue;}
        tmp_total_money_equip+=values.count*values.price;
        equipment_selected.push({"שם":values.name, "כמות":values.count})
    }
    elem = document.getElementById("payment-total");
    elem.value = tmp_total_money_equip;
    total = tmp_total_money_equip;


    // body of table with values
    equipment_selected.forEach(item => {
        bodyR = document.createElement('tr');
        for (const key in item) {
            bodyC = document.createElement('td');
            bodyC.classList.add("t-e-tbody");
            bodyC.textContent = item[key];
            bodyR.appendChild(bodyC);
        }
        parent.appendChild(bodyR);
    });
}
function closeModalAddLead(no_ask=0){
    if (no_ask || confirm("לבטל הוספת לקוח?")){
        $(document.getElementById("model-addlead")).fadeOut(100);
        $(document.getElementById("modaldes")).fadeIn(300);
        $(document.getElementById("modalstart")).fadeIn(300);
        document.getElementById("modalcontent").innerHTML = "";
        $(document.getElementById("modalcontent")).fadeOut(0);

    }
    else{

    }
}
function openModalAddLead(_this){
    $(document.getElementById("model-addlead")).fadeIn(300);
    if (document.getElementById("modalcontent").innerHTML!=""){return;}
    $.ajax({
        url:"/template/"+_this.id,
        type:"post",
        success:(res)=>{
            if (res.success){
                document.getElementById("aleadtitle").innerText = "הוספת לקוח לרשימות"
                document.getElementById("modaldes").innerText = res.welcome
                document.getElementById("modalcontent").innerHTML = res.template
                document.getElementById("closeModalButton").onclick = ()=>{closeModalAddLead();};
                supply_json = res.supply;
            }
            else{
                show_popup_error(res, _this);
            }
        }
    })

}

function showSearchLeads(_this){
    element = document.getElementById("searchleads");
    button = document.getElementById("opensearch");
    $(element).show(300);
    $(element).css("display", "flex");
    // replace call
    button.onclick = ()=>{hideSearchLeads(_this);};
    search_is_open.client =1;
}

function hideSearchLeads(_this){
    element = document.getElementById("searchleads");
    button = document.getElementById("opensearch");
    $(element).hide(300);
    button.onclick = ()=>{showSearchLeads(_this);};
    getTemplate($("#0")[0], 0, 1);
    search_is_open.client = 0;
}
function showModalContent(_this){
    $(document.getElementById("modaldes")).fadeOut(300)
    $(document.getElementById("modalstart")).fadeOut(300)
    $(document.getElementById("modalcontent")).fadeIn(300);
}
function searchLeads(_this, _type, t=0){
    element = document.getElementById("searchinput");
    value = element.value;
    if (!value){return;}
    bhtml = _this.innerHTML;
    _this.innerHTML = '<i class="fa-solid fa-atom fa-spin"></i>'
    $.ajax({
        url:"/search_lead/"+value,
        type:"post",
        data:{"type_search":_type, "template":t},
        success:(res)=>{
            if (res.success){
                templates[t].tmp = res.template;
                document.getElementsByClassName("dashboard-template")[0].innerHTML = res.template;
                if (t == 0){
                    showSearchLeads();
                }else if (t == 2){
                    showSearchHistory();
                }
                document.getElementById("searchinput").value = value;
            }
            else{
                show_popup_error(res, _this);
            }
            _this.innerHTML = bhtml;
        }
    })
}
function backAddLead(){
    $(document.getElementById("lead-summary")).fadeOut(300);
    $(document.getElementById("add-lead-form")).fadeIn(300);
}
function clientSummary(event, _this){
    event.preventDefault();
    $(_this).fadeOut(1);
    leadS   = document.getElementById("lead-summary");
    tableS  = document.getElementById("table-summary");
    array_values = [];
    var index = 0;
    for (i=0;i!=14;i++){o = _this.children[i];
        if(o.type != undefined && o.id != "equipment" && o.id != "submitaddlead"){
            console.log(o);
            array_values.push(o.value);
            elementK = tableS.children[0].children[index].children[0];
            elementV = tableS.children[0].children[index].children[1];
            elementV.innerText = o.value != "" ? o.value : "לא צוין";
            index+=1;
        }
        
    }

    $(leadS).fadeIn(300);
    updateTotalSummary($("#payment-safe"));
    createTableEquipmentSelected();

}

function setSafePayment(_this, number){
    result = (total/number).toFixed(2);
    element = document.getElementById("payment-safe");
    element.value = result;
}

function selectTypePay(_this, _type){
    last_button = document.getElementsByClassName("tpayb-selected")[0];
    if (!(last_button == undefined)){
       
        last_button.classList.remove("tpayb-selected");
        last_button.classList.add("tpayb")
    }

    element = document.getElementById("type-pay");
    element.value = _type;

    _this.classList.add("tpayb-selected");
    _this.classList.remove("tpayb");


}
function addLead(_this){
    text = _this.innerText
    loading(_this);
    $.ajax({
        url:"/add_lead",
        type:"POST",
        data:{
            "name":     document.getElementById("name").value,
            "phone":    document.getElementById("phone").value,
            "id_lead":  document.getElementById("lead_id").value,
            "supply" :  JSON.stringify(supply_json),
            "date":     document.getElementById("event-date").value,
            "location": document.getElementById("event-location").value,
            "sub_pay":  document.getElementById("payment-safe").value,
            "payment":  document.getElementById("payment-total").value,
            "exp_fuel": document.getElementById("exp-fuel").value,
            "exp_employee": document.getElementById("exp-employee").value,
            "type_pay": document.getElementById("type-pay").value
        },
        success:(res)=>{
            if (res.success){
                closeModalAddLead(no_ask=1);
                getTemplate($("#0")[0], "0", 1);

            }else{
                alert(res.title + "   "+ res.notice) ;

            }
            unloading(_this, text);
        }
    })
}
function showEquipmentBySearch(word){
    ListE = document.getElementById("list-equipment");
    ListE.innerHTML = "";
    for ([key, value] of Object.entries(supply_json)){
        if (value.name.indexOf(word) > -1 && word.length > 0){
            // box
            boxE = document.createElement('div');
            boxE.classList.add('box-equipment');
            boxE.id = value.id;
            // name of equipment
            nameE = document.createElement('p');
            nameE.classList.add('box-equipment-title');
            nameE.textContent = value.name;
            // price of equipment
            priceE = document.createElement('span');
            priceE.textContent = value.price + "₪";
            // action of add or remove 1 value 
            LEAction = document.createElement('div');
            LEAction.classList.add('list-equipment-action');
            // plus
            PButton = document.createElement('button');
            PButton.id = 'plus';
            PButton.type = 'button';
            PButton.classList.add('button-equipment');
            PButton.innerHTML = '<i class="fa-solid fa-plus"></i>';
            PButton.onclick = function(){addEquipmentToList(this, 1);}
            // count of specific 
            countE = document.createElement('span');
            countE.id = 'count-equipment';
            countE.textContent = value.count;

            const MButton = document.createElement('button');
            MButton.id = 'minus';
            MButton.type = 'button';
            MButton.classList.add('button-equipment');
            MButton.innerHTML = '<i class="fa-solid fa-minus"></i>';
            // onclick
            MButton.onclick = function(){addEquipmentToList(this, -1);}

            LEAction.appendChild(PButton);
            LEAction.appendChild(countE);
            LEAction.appendChild(MButton);

            boxE.appendChild(nameE);
            boxE.appendChild(priceE);
            boxE.appendChild(LEAction);
            ListE.appendChild(boxE);
        }
    }
}
function addEquipmentToList(_this, number){
    nums = _this.parentElement.children[1];
    nadd = parseInt(nums.textContent);
    equipment = supply_json[_this.parentElement.parentElement.id];
    if (!nadd && number == -1){return;}
    nums.innerText = nadd += number;
    supply_json[_this.parentElement.parentElement.id].count = parseInt(nums.innerText);
}
function updateTotalSummary(_this){
    if (!_this.value){_this.value=0;}
    identify_total[_this.id]=_this.value;
    var values = get_summery_exp();
    elem = document.getElementById("payment-total");
    elem.value = (total+values) ;
}

function get_summery_exp(){
    values=0;
    var idens = Object.values(identify_total);
    idens.forEach(function(value) {values+=parseFloat(value)});
    return values;
}

function leadAction(value, _ty){
    if (_ty == 0){
        location.href = "tel:"+value;
    }
    else if (_ty == 1){
        location.href = encodeURI(value);
    }else if (_ty == 2){
        window.open(value, "_blank");
    }
    
}

function showMenuLeadAction(_this){
    _this.textContent = "סגירה "
    li = _this.nextElementSibling;
    li.style.display = 'block';
    _this.onclick = function(){
        closeMenuLeadAction(_this)
    }
}
function closeMenuLeadAction(_this){
    _this.textContent = "פעולות"
    li = _this.nextElementSibling;
    li.style.display = 'none';
    _this.onclick = function(){
        showMenuLeadAction(_this)
    }
}

/**
 * @type setInterval
 */
var TIMER = null;
/**
 * 
 * @param {String} ctime 
 * @returns {dick}
 */
function countdown(ctime){
    if (TIMER){
        clearInterval(TIMER);
        TIMER = null;
        countdown(ctime);
        return;
    }
    /* interval to countdown */
    var _countdown = new Date(ctime).getTime();
    TIMER = setInterval(function(){
        var ctime_now = new Date().getTime();
        var distance = _countdown - ctime_now;
        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

        if (distance < 0 || isNaN(distance)) {
            clearInterval(TIMER);
            days = "00";
            hours = "00";
            minutes = "00";
            seconds = "00";

        };
        // end of story
        // document.getElementById("lnkd").innerText = days;
        // document.getElementById("lnkh").innerText = hours;
        document.getElementById("lnkm").innerText = minutes;
        document.getElementById("lnks").innerText = seconds;

    }, 999)

}


function logout(){
    $.ajax({
        url:"/l0g0ut",
        success:(res)=>{
            if (res.success){
                location.href="/";
            }
            else{
                show_popup_error(res, null);
            }
        }
    })
}

/***
 * show alert 
 */


modal_show = document.getElementById("modal-show")


window.onclick = function(event) {
    try{
        if (event.target != document.getElementsByClassName("lbt-options")[0]){
            document.getElementById("menu-action-li").style.display = 'none'
        }
    }catch{

    }
}




