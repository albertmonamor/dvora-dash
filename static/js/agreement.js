
var signatureO = new SignaturePad(document.getElementById('sig-owner'));
var signatureC = new SignaturePad(document.getElementById('sig-client'));


function clearSignature(parent){
    if (parent == "sig-owner"){
        signatureO.clear();
    }
    else{
        signatureC.clear();
    }
}