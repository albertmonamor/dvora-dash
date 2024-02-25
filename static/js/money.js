
interval_id = 0
json_exp_inc=  []
MAX_exp_inc = 30000
MIN_exp_inc = 2
type_graph = 'year'
type_gapi  = 2
const listen = new IntersectionObserver(showGraphAgain, {
    root: null, 
    rootMargin: '0px',
    threshold: 0.0, 
});



const json_monts_year = {
     "1": "ינואר" , 2: "פברואר" ,
    3: "מרץ" ,  4: "אפריל" , 
    5: "מאי" , 6: "יוני" ,
    7: "יולי" , 8: "אוגוסט" , 
    9: "ספטמבר" ,10: "אוקטובר" ,
    11: "נובמבר" ,12: "דצמבר" }


// Function to handle the intersection observer callback
function showGraphAgain(entries) {
    entries.forEach((entry) => {
      if (entry.isIntersecting && getLastTemplate() == '3') {
        setJson(type_gapi);
        setValuesGraphEAP(type_graph);
        
      }
    });
  }

listen.observe(document.getElementById("footer-dashboard"))
 


/**
 * 
 * @param {Element} t 
 */
function filter_date(t){

}


// ----------------- charts ---------------------


async function setValuesGraphEAP(type='year'){
    type_graph = type
    parent = document.getElementById("pgraph-money")
    sparent = document.getElementById("graph-money") 
    fparent = document.getElementById("footer-labels");
    if (!parent){return;}
    
    sparent.innerHTML='';
    fparent.innerHTML='';
    if (type == 'year'){
        fparent.classList.remove('graph-month')
        sparent.classList.remove('graph-month')
        sparent.classList.add("graph-year")
        fparent.classList.add('graph-year')

        for ( value of json_exp_inc)
        {
            div = document.createElement("div")
            div.classList.add('money-item')
            span1 = document.createElement('span')
            span1.title='הכנסות'
            span1.style.height = `${MIN_exp_inc+parseInt((100*value.json.p)/MAX_exp_inc)}px`
            span1.classList.add('i')
            span1.classList.add('width-year')
            span1.id = value.json.p
            span1.onmouseover= function(){showGraphMenu()}
            span2 = document.createElement("span")
            span2.title='הוצאות'
            span2.style.height = `${MIN_exp_inc+parseInt((100*value.json.e)/MAX_exp_inc)}px`
            span2.classList.add('e')
            span2.classList.add('width-year')
            span2.id = value.json.e
            div.appendChild(span1)
            div.appendChild(span2)
            sparent.appendChild(div);
            footer_span = document.createElement("span")
            footer_span.textContent = json_monts_year[value.month];
            footer_span.role = value.month
            footer_span.onclick = function(){showGraphByMonth(this)}
            fparent.appendChild(footer_span);
            $(span1).show(300)
            $(span2).show(400)

        }
    }
    else if (type == 'month'){
        sparent.classList.add("graph-month")
        fparent.classList.add('graph-month')
        sparent.classList.remove('graph-year')
        fparent.classList.remove('graph-year')
        for ([index, value] of Object.entries(json_exp_inc)){
            div = document.createElement("div")
            div.classList.add('money-item')
            span1 = document.createElement('span')
            span1.title='הכנסות'
            span1.style.height = `${MIN_exp_inc+parseInt((200*value.json.p)/MAX_exp_inc)}px`
            span1.classList.add('i')
            span1.classList.add('width-month')
            span1.id = value.json.p
            span1.onmouseover= function(){showGraphMenu()}
            span2 = document.createElement("span")
            span2.title='הוצאות'
            span2.style.height = `${MIN_exp_inc+parseInt((200*value.json.e)/MAX_exp_inc)}px`
            span2.classList.add('e')
            span2.classList.add('width-month')
            span2.id = value.json.e
            div.appendChild(span1)
            div.appendChild(span2)
            sparent.appendChild(div);
            footer_span = document.createElement("span")
            if (1){
                footer_span.textContent = value.day;
            }  
            fparent.appendChild(footer_span);
            $(span1).show(300)
            $(span2).show(300)
        }
    }
}


function sleep(ms) {
    return new Promise(fuck_you => setTimeout(fuck_you, ms));
  }


function setJson(g=2, month=0){
    $.ajax({
        url:"/money/"+g,
        type:"post",
        data:{"month":month},
        success:(res)=>{
            if (res.success){
                json_exp_inc = res.json;
                setValuesGraphEAP(type_graph);
            }
            else{
                popNotice("error", res.title, res.notice);
            }
        }
    })

}

function showGraphMenu(){
    m = document.getElementById("menu-on-graph")
    m.style.display = 'flex';
}
function closeGraphMenu(){
    m = document.getElementById("menu-on-graph")
    m.style.display = 'none';
}
function moveMenu(event){
    menu = document.getElementById('menu-on-graph');
    
    menu.style.left = parseInt(event.clientX-130) + 'px';
    menu.style.top = (parseInt(event.clientY)-134) + 'px';
    e = document.elementFromPoint(event.clientX, event.clientY);
    
    if (e.classList.contains('i') || e.classList.contains('e')){
        if (e.classList.contains('e')){
            classes1 = 'm-g-title m-g-t-r'
        }
        else{
            classes1 = 'm-g-title m-g-t-g'
        }
        menu.innerHTML = `
        <span class='${classes1}'>${e.title}</span>
        <span class='m-g-m'>₪${e.id.replace(/\B(?=(\d{3})+(?!\d))/g, ",")}</span>
        `;
    }
}

function showGraphFilter(t, api){
    type_graph = t.role
    elems = document.getElementsByClassName("bfselcted")[0];
    elems.classList.remove("bfselcted");
    t.classList.add("bfselcted")
    type_gapi = api
    setJson(type_gapi)
    
}
function showGraphByMonth(_this){
    type_gapi = 1
    type_graph = 'month'
    setJson(1, _this.role);
}