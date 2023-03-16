const int_to_str = {
    "1":"l0", 
    "2":"l2",
    "3":"l3",
    "4":"l4",
    "5":"l5",
    "6":"l6",
    "7":'l7', 
    "8":"l8",
    "9":"l9",
    "10":"l10"
}

function ShowProgressStatus(lvl){
    for (i =1; i < 11; i++){
        element = document.querySelector("."+int_to_str[i]);
        if ((lvl+1) > i){
            element.classList.add("p-active")
            continue;
        }
        element.classList.remove("p-active")
    }

}