async function getUserInfo(){
    let resp = await fetch('/getnow/user');
    resp = await resp.json();
    return resp;
}

async function getData(req){
    let respn = await fetch('/getnow/' + req);
    respn = await respn.json();
    return respn;
}