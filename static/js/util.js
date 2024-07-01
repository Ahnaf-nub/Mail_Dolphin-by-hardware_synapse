async function makeChart(chartID) {
    const datas = await getData('emails');
    const ctx = document.getElementById(chartID);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: datas['dates'],
            datasets: [{
                label: 'Emails Per Day',
                data: datas['num'],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}


async function showTrainingData(){
    let trainingDat = await getData('training');
    showGeninfo(trainingDat["general"]);
    showSpecReply(trainingDat["spec"]);
    showContFilter(trainingDat["mailContacts"]);
    showIntFilter(trainingDat["mailIntents"]);
}

function showGeninfo(info){
    document.querySelector("#generalInfoInput").textContent = info;
}

let numSpec = 0;
let specList = [];
function showSpecReply(info){
    let container = document.querySelector("#specAccordion");
    let template = document.querySelector('#specTemplate')
    template.style.display="none";

    for(numSpec = 0; numSpec < info.length; numSpec++){
        let _info = info[numSpec];
        let newSpec = addSpecReply(template, container, numSpec);
        newSpec.querySelector('.replyDesc').value = _info["name"];
        newSpec.querySelector('.tuningInSub').value = _info["input"]["subject"];
        newSpec.querySelector('.tuningInBody').value = _info["input"]["body"];
        newSpec.querySelector('.tuningOutBody').value = _info["output"]["body"];
        specList.push(newSpec);
    }
    numSpec -= 1;
}

function addSpecReply(template, parent, id){
    let clone = template.cloneNode(true);
    clone.id = `spec-${id}`;
    clone.setAttribute('name', `spec-${id}`);
    clone.querySelector('.accordion-button').setAttribute('data-bs-target', `#collapse-${id}`);
    clone.querySelector('.accordion-button').setAttribute('aria-controls', `collapse-${id}`);
    clone.querySelector('.accordion-collapse').setAttribute('id', `collapse-${id}`);

    clone.querySelector('.deleteBtn').setAttribute('id', `delete-${id}`);
    clone.querySelector('.dupliBtn').setAttribute('id', `dupli-${id}`);

    clone.querySelector('.replyDesc').setAttribute('id', `name-${id}`);
    clone.querySelector('.tuningInSub').setAttribute('id', `inSub-${id}`);
    clone.querySelector('.tuningInBody').setAttribute('id', `inBody-${id}`);
    clone.querySelector('.tuningOutBody').setAttribute('id', `outBody-${id}`);

    clone.querySelector('.deleteBtn').addEventListener('click', ()=>{
        
        if(document.querySelector('#specAccordion').childElementCount > 2){ 
            clone.remove();
            specList[id] = null;
        }
    });
    clone.querySelector('.dupliBtn').addEventListener('click', ()=>{
        numSpec += 1;
        let newSpec = addSpecReply(clone, parent, numSpec);
        newSpec.querySelector('.replyDesc').value = "(Unnamed)";
        specList.push(newSpec);

        clone.querySelector('.accordion-button').setAttribute('aria-expanded', "false");
        clone.querySelector('.accordion-button').setAttribute('class', "accordion-button collapsed");
        clone.querySelector('.accordion-collapse').setAttribute('class', "accordion-collapse collapse");
        window.location.href = '#specReply'
    });

    clone.style.display = 'block';
    parent.prepend(clone);

    return clone;
}

function addNewSpecReply(){
    let container = document.querySelector("#specAccordion");
    let template = document.querySelector('#specTemplate')
    template.style.display="none";

    numSpec += 1;
    let newSpec = addSpecReply(template, container, numSpec);
    newSpec.querySelector('.replyDesc').value = "(Unnamed)";
    specList.push(newSpec);
}

let contacts = [];
function showContFilter(info){
    let txt = "";
    contacts = info['contacts']
    for(let i = 0; i < contacts.length; i++){
        txt = txt + contacts[i] + ", ";
    }
    console.log(txt);
    document.querySelector('#contacts').value = txt;

    document.querySelector('#cTrue').checked = info['reply'];
    document.querySelector('#cFalse').checked = !info['reply'];
    
}

function contactsFilter(_text){
    contacts = _text.split(",").map(function (value) {
        return value.trim();
    });
    for(let i = contacts.length-1; i>=0; i--){
        if(contacts[i] == ''){
            contacts.splice(i, 1);
        }
    }
}

let intents = [];
function showIntFilter(info){
    let txt = "";
    intents = info['intents']
    for(let i = 0; i < intents.length; i++){
        txt = txt + intents[i] + "\n\n";
    }
    console.log(txt);
    document.querySelector('#intents').value = txt;

    document.querySelector('#iTrue').checked = info['reply'];
    document.querySelector('#iFalse').checked = !info['reply'];
}

function intentsFilter(_text){
    intents = _text.split("\n").map(function (value) {
        return value.trim();
    });
    for(let i = intents.length-1; i>=0; i--){
        if(intents[i] == '' || intents[i].length < 10){
            intents.splice(i, 1);
        }
    }
}



async function saveData(){
    console.log("Saving Data");

    let data = getTrainingDataUser();

    fetch('/userData/trainData', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(res => res.json()).then(data => {
        console.log(data);
        if(data['message'] == 'Data received!'){
            console.log("Saved");
        }
    });
}

function getTrainingDataUser(){
    let trainingDat = {
        general: document.querySelector("#generalInfoInput").value,
        specReply: {
            specReply:[]
        },
        mailContacts: {
            reply: true,
            contacts: []
        },
        mailIntents: {
            reply: true,
            intents: []
        }
    };

    for(let i = 0; i < specList.length; i++){
        let specCard = specList[i];
        if(specCard){
            trainingDat.specReply.specReply.push({
                name: specCard.querySelector('.replyDesc').value,
                input: {
                    subject: specCard.querySelector('.tuningInSub').value,
                    body: specCard.querySelector('.tuningInBody').value
                },
                output: {
                    body: specCard.querySelector('.tuningOutBody').value
                }
            });
        }
    }

    let cRadio = document.querySelector('input[name="filterContacts"]:checked').id;
    trainingDat.mailContacts.contacts = contacts;
    trainingDat.mailContacts.reply = (cRadio == 'cTrue')? true : false;

    let iRadio = document.querySelector('input[name="filterIntents"]:checked').id;
    trainingDat.mailIntents.intents = intents;
    trainingDat.mailIntents.reply = (iRadio == 'iTrue')? true : false;

    console.log(trainingDat);

    return trainingDat;
}


function testEmail(sub, body, replyLabel){
    data = {
        subject: sub,
        body: body
    }

    fetch('/userData/testEmail', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(res => res.json()).then(dat => {
        let reply = dat['reply'];
        replyLabel.textContent = reply;
    });
}